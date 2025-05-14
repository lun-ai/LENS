% Circuit representation in Prolog
% Circuit gates (AND gates with one input) labelled with numbers
gate(101).
gate(102).
gate(103).
gate(104).
gate(201).
gate(202).
gate(203).
gate(204).
gate(205).
gate(301).
gate(302).
gate(303).
gate(304).
gate(305).
gate(306).
gate(401).
gate(402).
gate(403).
gate(404).
gate(405).
gate(406).
gate(407).
gate(501).
gate(502).
gate(503).
gate(504).
gate(505).
gate(506).
gate(507).
gate(601).
gate(602).
gate(603).
gate(604).
gate(605).
gate(606).
gate(607).
gate(608).
gate(701).
gate(702).
gate(703).
gate(704).
gate(705).
gate(706).
gate(707).
gate(708).
gate(709).
gate(710).
gate(801).
gate(802).
gate(803).
gate(901).
gate(902).
gate(903).
gate(904).
gate(1001).
gate(1002).
gate(1003).
gate(1004).
gate(1005).
gate(1101).
gate(1102).
gate(1103).
gate(1104).
gate(1105).
gate(1106).
gate(1201).
gate(1202).
gate(1203).
gate(1204).
gate(1205).
gate(1206).
gate(1301).
gate(1302).
gate(1303).
gate(1304).
gate(1305).
gate(1306).
gate(1307).
gate(1401).
gate(1402).
gate(1403).
gate(1404).
gate(1405).
gate(1406).
gate(1407).
gate(1408).

% All terminals (light bulbs)
% gate(105).
% gate(206).
% gate(307).
% gate(408).
% gate(508).
% gate(609).
% gate(711).
% gate(804).
% gate(905).
% gate(1006).
% gate(1107).
% gate(1207).
% gate(1308).
% gate(1409).
terminal(105).
terminal(206).
terminal(307).
terminal(408).
terminal(508).
terminal(609).
terminal(711).
terminal(804).
terminal(905).
terminal(1006).
terminal(1107).
terminal(1207).
terminal(1308).
terminal(1409).

% Connections between gate and terminal
is_connected(103,105).
is_connected(104,105).
is_connected(205,206).
is_connected(305,307).
is_connected(407,408).
is_connected(406,408).
is_connected(506,508).
is_connected(507,508).
is_connected(608,609).
is_connected(607,609).
is_connected(605,609).
is_connected(706,711).
is_connected(710,711).
is_connected(708,711).
is_connected(803,804).
is_connected(904,905).
is_connected(1004,1006).
is_connected(1005,1006).
is_connected(1106,1107).
is_connected(1206,1207).
is_connected(1307,1308).
is_connected(1408,1409).
is_connected(1407,1409).

% Connections between gates
is_connected(101,102).
is_connected(101,103).
is_connected(102,104).
is_connected(202,203).
is_connected(203,204).
is_connected(201,205).
is_connected(204,205).
is_connected(301,303).
is_connected(302,303).
is_connected(303,304).
is_connected(304,305).
is_connected(305,306).
is_connected(401,405).
is_connected(402,405).
is_connected(403,406).
is_connected(404,406).
is_connected(405,407).
is_connected(501,502).
is_connected(502,503).
is_connected(503,504).
is_connected(503,505).
is_connected(504,506).
is_connected(505,507).
is_connected(601,603).
is_connected(602,603).
is_connected(602,604).
is_connected(602,605).
is_connected(603,606).
is_connected(604,607).
is_connected(606,608).
is_connected(701,702).
is_connected(701,703).
is_connected(702,704).
is_connected(703,705).
is_connected(704,706).
is_connected(702,707).
is_connected(705,707).
is_connected(705,708).
is_connected(707,709).
is_connected(709,710).
is_connected(801,802).
is_connected(802,803).
is_connected(901,902).
is_connected(902,904).
is_connected(903,904).
is_connected(1001,1004).
is_connected(1002,1004).
is_connected(1002,1005).
is_connected(1003,1005).
is_connected(1101,1104).
is_connected(1102,1104).
is_connected(1103,1105).
is_connected(1104,1106).
is_connected(1105,1106).
is_connected(1202,1203).
is_connected(1201,1204).
is_connected(1203,1204).
is_connected(1204,1205).
is_connected(1205,1206).
is_connected(1301,1302).
is_connected(1302,1304).
is_connected(1304,1305).
is_connected(1303,1306).
is_connected(1305,1306).
is_connected(1306,1307).
is_connected(1401,1403).
is_connected(1403,1404).
is_connected(1402,1405).
is_connected(1404,1406).
is_connected(1405,1407).
is_connected(1406,1408).
