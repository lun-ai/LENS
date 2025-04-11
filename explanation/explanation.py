# Import necessary libraries
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser

# Install Ollama (if not already installed)
# curl -fsSL https://ollama.com/install.sh | sh

# Start the Ollama server
# ollama serve


# Define the output structure with a Pydantic model
class PrologExplanation(BaseModel):
    summary: str = Field()
    primitive: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of primitives with their descriptions",
        example=[{"name": "odd", "description": "Checks if a number is odd"},]
    )
    explanation: str = Field()

    def get_explanation(self) -> str:
        """Return a formatted string of the explanation.

        Returns:
            str: Formatted explanation string
        """
        # Start with the summary
        result = f"Summary: {self.summary}\n\n"

        # Add the primitives
        result += "Primitives:\n"
        for pred in self.primitive:
            result += f"- {pred.get('name')}: {pred.get('description')}\n"

        # Add the explanation
        result += f"\nExplanation: {self.explanation}\n"

        return result


def explain_prolog(llm, prompt_template, prolog_code, variables=['prolog_code']):
    """Generate a natural language explanation of a Prolog program.

    Args:
        llm: The language model to use
        prompt: The prompt template to use
        prolog_code (str): The Prolog code to explain

    Returns:
        PrologExplanation: Structured explanation of the Prolog program
    """
    # Initialize the output parser
    parser = PydanticOutputParser(pydantic_object=PrologExplanation)

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=variables,
        partial_variables={"JSON_format": parser.get_format_instructions()}
    )

    # Get raw string response from the LLM
    chain = prompt | llm | StrOutputParser()
    raw_result = chain.invoke({"prolog_code": prolog_code})

    print(f"===== Generated Raw Text =====\n{raw_result}")

    # Parse the raw string into a structured PrologExplanation object
    try:
        # Try to parse the output directly
        parsed_result = parser.parse(raw_result)

        # print(f"\n===== Parsed Prolog Explanation =====\n{parsed_result}")
        print(f"\n===== Parsed Text =====")

        print(f"Summary: {parsed_result.summary}\n")
        print("Primitives:")
        for pred in parsed_result.primitive:
            print(f"- {pred.get('name')}: {pred.get('description')}")
        print(f"\nExplanation: {parsed_result.explanation}\n")
        return parsed_result
    except Exception as e:
        # If direct parsing fails, attempt to extract structured data from text
        print(f"Parsing error: {e}")
        print("Returning raw output instead. Check format of LLM response.")
        return raw_result


def compose_prolog_input(task_names: list[str], comments=True):

    prolog_prompt_template = """

%%%%%%%%%%%%%%%%%%%% Target rules %%%%%%%%%%%%%%%%%%%%
{target_rules}

%%%%%%%%%%%%%%%%%%%% Primitives %%%%%%%%%%%%%%%%%%%%
{primitives}

%%%%%%%%%%%%%%%%%%%% Biases %%%%%%%%%%%%%%%%%%%%
{biases}

"""
    target_rules = ''
    primitives = ''
    biases = ''
    for task in task_names:
        with open(f'{task}/target.pl', 'r') as file:
            lines = file.readlines()
            if not comments:
                lines = [line for line in lines if not line.startswith('%')]

            # Skip input lines
            lines = [line for line in lines if not line.startswith(
                ':-')]
            target_rules += '\n' + ''.join(lines)

        with open(f'{task}/prim.pl', 'r') as file:
            lines = file.readlines()
            if not comments:
                lines = [line for line in lines if not line.startswith('%')]

            # Skip input lines
            lines = [line for line in lines if not line.startswith(
                ':-')]
            primitives += '\n' + ''.join(lines)

        with open(f'{task}/bias.pl', 'r') as file:
            lines = file.readlines()
            if not comments:
                lines = [line for line in lines if not line.startswith('%')]

            # Include input and output signature direction declarations
            lines = [line for line in lines if 'direction' in line]

            biases += '\n' + ''.join(lines)

    prolog_code = prolog_prompt_template.format(
        target_rules=target_rules,
        primitives=primitives,
        biases=biases
    )

    print(prolog_code)

    return prolog_code


def structured_prompt(llm, task_names, template_path, explanation_path, sample_size=10):
    """Prompt the LLM to explain the Prolog program.
    Args:
        llm: The language model to use
        task_names (list): List of task names
        template_path (str): Path to the explanation template
        explanation_path (str): Path to save the explanation
        sample_size (int): Number of samples to generate
    Returns:
        str: Formatted explanation or None if error
    """

    explanations = []
    success = 0
    i = 0
    while i < sample_size:
        try:
            prolog_input = compose_prolog_input(task_names, comments=False)
            with open(template_path, 'r') as file:
                explanation_template = file.read()
            result = explain_prolog(llm, explanation_template, prolog_input)

            if isinstance(result, PrologExplanation):
                explanation_text = result.get_explanation()
                explanations.append(
                    f'%%%%%%%%%%%%%%%%%%%% Sample {i+1} %%%%%%%%%%%%%%%%%%%%')
                explanations.append(explanation_text)
                print(f"------> Sample {i+1} complete")
                success += 1
            else:
                print(f"------> Sample {i+1} failed to parse")

        except Exception as e:
            print(f"Error in sample {i+1}: {e}")

        # Ensure we always have the same number of successful samples
        i += 1

    # Write all explanations to the output file
    if explanations and explanation_path:
        with open(explanation_path, 'w') as file:
            file.write(
                "%%%%%%%%%%%%%%%%%%%% Successful Samples %%%%%%%%%%%%%%%%%%%%\n")
            file.write("\n\n".join(explanations))

    print(f"\n------> All samples written to {explanation_path}")
    print(f"------> Total samples: {sample_size}")
    print(f"------> Successful samples: {success}")


def unstructured_prompt(llm, task_names, template_path, explanation_path, sample_size=10):
    """Prompt the LLM to explain the Prolog program with an unstructured, natural language response.

    Args:
        llm: The language model to use
        task_names (list): List of task names
        template_path (str): Path to the explanation template
        explanation_path (str): Path to save the explanation
        sample_size (int): Number of samples to generate

    Returns:
        list: List of generated explanations
    """
    explanations = []
    success = 0
    i = 0

    while i < sample_size:
        try:
            # Get the Prolog code
            prolog_input = compose_prolog_input(task_names, comments=False)

            # Read the template file
            with open(template_path, 'r') as file:
                explanation_template = file.read()

            # Replace the [PROLOG CODE] placeholder with actual code
            prompt_template = explanation_template.replace(
                "[PROLOG CODE]", prolog_input)

            # Create a simple chain for unstructured output
            chain = PromptTemplate(
                template=prompt_template, input_variables=[]) | llm | StrOutputParser()

            # Generate the explanation
            raw_explanation = chain.invoke({})

            print(
                f"===== Generated Explanation {i+1} =====\n{raw_explanation}\n")

            # Add to explanations list
            explanations.append(
                f'%%%%%%%%%%%%%%%%%%%% Sample {i+1} %%%%%%%%%%%%%%%%%%%%')
            explanations.append(raw_explanation)
            print(f"------> Sample {i+1} complete")
            success += 1

        except Exception as e:
            print(f"Error in sample {i+1}: {e}")

        i += 1

    # Write all explanations to the output file
    if explanations and explanation_path:
        with open(explanation_path, 'w') as file:
            file.write(
                "%%%%%%%%%%%%%%%%%%%% Unstructured Explanations %%%%%%%%%%%%%%%%%%%%\n")
            file.write("\n\n".join(explanations))

    print(f"\n------> All explanations written to {explanation_path}")
    print(f"------> Total samples: {sample_size}")
    print(f"------> Successful samples: {success}")

    return explanations
