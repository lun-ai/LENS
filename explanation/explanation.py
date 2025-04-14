# Import necessary libraries
import anthropic
from openai import OpenAI
from langchain.schema.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
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


def compose_prolog_input(task_names: list[str], comments=True, biases=True) -> str:

    #     prolog_prompt_template = """

    # %%%%%%%%%%%%%%%%%%%% Target rules %%%%%%%%%%%%%%%%%%%%
    # {target_rules}

    # %%%%%%%%%%%%%%%%%%%% Primitives %%%%%%%%%%%%%%%%%%%%
    # {primitives}

    # """
    #     if biases:
    #         prolog_prompt_template += """
    # %%%%%%%%%%%%%%%%%%%% Biases %%%%%%%%%%%%%%%%%%%%
    # {biases}

    # """

    prolog_prompt_template = """

%%%%%%%%%%%%%%%%%%%% Main program %%%%%%%%%%%%%%%%%%%%
{target_rules}

%%%%%%%%%%%%%%%%%%%% Primitives %%%%%%%%%%%%%%%%%%%%
{primitives}

"""
    if biases:
        prolog_prompt_template += """
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

    # print(prolog_code)

    return prolog_code


def prompt_structured_output(llm, task_names, template_path, explanation_path, sample_size=10):
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


def instruct_prompt_output(llm, task_names, explanation_path, sample_size=10):
    """Prompt the LLM to explain the Prolog program with an unstructured, natural language response.

    Args:
        llm: The language model to use
        task_names (list): List of task names
        explanation_path (str): Path to save the explanation
        sample_size (int): Number of samples to generate

    Returns:
        list: List of generated explanations
    """
    explanations = []
    success = 0
    i = 0

    # Read the template once
    template_path = 'explanation/explanation_template_instruct.txt'
    with open(template_path, 'r') as file:
        explanation_template = file.read()

    # Check if the template has an [INSTRUCTION] placeholder
    if "[INSTRUCTION]" not in explanation_template:
        print(
            f"Warning: Template at {template_path} doesn't contain [INSTRUCTION] placeholder.")
        return []

    while i < sample_size:
        try:
            # Get the Prolog code
            prolog_input = compose_prolog_input(
                task_names, comments=False, biases=False)

            # Read the instruction content
            with open('explanation/instruction.txt', 'r') as file:
                instruction = file.read()

            # Insert the instruction into the template
            # Replace [PROLOG CODE] in the instruction with the actual code
            prompt_template = explanation_template.replace(
                "[INSTRUCTION]", instruction).replace("[PROLOG CODE]", prolog_input)

            print(f"===== Prompt {i+1} =====\n{prompt_template}\n")

            # Create a simple chain for unstructured output
            chain = PromptTemplate(
                template=prompt_template, input_variables=[]) | llm | StrOutputParser()

            # Generate the explanation
            explanation = chain.invoke({})

            # Extract content after "Response:" if present
            # if "Response:" in raw_explanation:
            #     explanation_part = raw_explanation.split("Response:")[
            #         1].strip()
            # else:
            #     explanation_part = raw_explanation

            print(
                f"===== Generated Explanation {i+1} =====\n{explanation}\n")

            # Add to explanations list
            explanations.append(
                f'%%%%%%%%%%%%%%%%%%%% Sample {i+1} %%%%%%%%%%%%%%%%%%%%')
            explanations.append(explanation)
            print(f"------> Sample {i+1} complete")
            success += 1

        except Exception as e:
            print(f"Error in sample {i+1}: {e}")
            print(f"Error details: {str(e)}")

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


def user_prompt_output(llm, task_names, explanation_path, sample_size=10):
    """Prompt the LLM using the v3 template format designed for chat models like Starcoder2.

    Args:
        llm: The language model to use
        task_names (list): List of task names
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
            prolog_input = compose_prolog_input(
                task_names, comments=False, biases=False)

            # Create instruction with Prolog code
            with open('explanation/instruction.txt', 'r') as file:
                instruction = file.read()

            # Remove the Instruction and response key word
            instruction = instruction.replace(
                "Instruction: ", "").replace("Response:", "")

            with open('explanation/explanation_template_instruct.txt', 'r') as file:
                explanation_template = file.read()

            explanation_template = explanation_template.replace(
                "[INSTRUCTION]", instruction).replace("[PROLOG CODE]", prolog_input)

            # Format for starcoder2 using message-based approach
            # For v3 template, we need to use chat messages instead of a simple template
            chat_messages = [HumanMessage(
                role='user', content=explanation_template)]

            # Create a chat template that handles the special formatting
            chat_prompt = ChatPromptTemplate.from_messages(chat_messages)

            print(f"===== Prompt {i+1} =====\n{explanation_template}")

            # Create chain for output
            chain = chat_prompt | llm | StrOutputParser()

            # Generate the explanation
            explanation = chain.invoke({})

            # Clean up response if needed - some models might include "### Response" markers
            # if "### Response" in explanation:
            #     explanation = explanation.split("### Response")[1].strip()

            print(
                f"===== Generated Explanation {i+1} =====\n{explanation}\n")

            # Add to explanations list
            explanations.append(
                f'%%%%%%%%%%%%%%%%%%%% Sample {i+1} %%%%%%%%%%%%%%%%%%%%')
            explanations.append(explanation)
            print(f"------> Sample {i+1} complete")
            success += 1

        except Exception as e:
            print(f"Error in sample {i+1}: {e}")

        i += 1

    # Write all explanations to the output file
    if explanations and explanation_path:
        with open(explanation_path, 'w') as file:
            file.write(
                "%%%%%%%%%%%%%%%%%%%% Chat Template Explanations %%%%%%%%%%%%%%%%%%%%\n")
            file.write("\n\n".join(explanations))

    print(f"\n------> All explanations written to {explanation_path}")
    print(f"------> Total samples: {sample_size}")
    print(f"------> Successful samples: {success}")

    return explanations


def summary_prompt_output(samples, summary_path, api, max_tokens=4096, temperature=0, targets=['linear_path', 'partition', 'partition_sizes', 'optimal_partition_sizes']):

    with open('explanation/summary_template.txt', 'r') as file:
        template = file.read()

    with open(samples, 'r') as file:
        samples = file.read()

    prompt = template.replace("[SAMPLES]", samples).replace(
        "[TARGETS]", "\"" + "\", \"".join(targets) + "\"")

    if "claude" in api['model']:
        client = anthropic.Anthropic(api_key=api['api_key'])
        response = client.messages.create(
            model=api['model'],
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.content
    else:
        client = OpenAI(
            api_key=api['api_key'],
            base_url=api['api_url']
        )
        response = client.chat.completions.create(
            model=api['model'],
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        summary = response.choices[0].message.content

    print(f"===== Summary =====\n{summary}")
    with open(summary_path, 'w') as file:
        file.write(
            "%%%%%%%%%%%%%%%%%%%% Summary %%%%%%%%%%%%%%%%%%%%\n")
        file.write(summary)
