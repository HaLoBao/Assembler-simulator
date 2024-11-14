
from assembler_paser import assemly_parser
from register_table import register_table
from instruction_table import instruction_table

file = open('riscv1.asm')
content = []
for line in file:
    line = line.strip()
    content.append(line)
parse_instructions = assemly_parser(instruction_table,register_table)
parse_instructions.build_label_table(content)
parse_instructions.Pass(content)




