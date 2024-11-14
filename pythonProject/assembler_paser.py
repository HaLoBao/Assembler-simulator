
import re
class assemly_parser:
    # Word size
    word_size = 4
    # List of labels and their respective locations
    symbol_table = dict()
    # current instruction table
    instruction_table = dict()
    # vị trí hiện tại trong bộ nhớ
    current_location = 0
    # current symbol table
    register_table = dict()
    # Output
    output_array = []
    def __init__(self, instruction_table, register_table):
        self.instruction_table = instruction_table
        self.register_table = register_table
        self.word_size = 4
        self.current_location = 64

    # danh sách lable và địa chỉ nhớ
    def build_label_table(self, lines):
        for line in lines:
            if ':' in line:
                lable = line[0:line.find(':')]
                self.symbol_table[lable] = self.current_location
            self.current_location += self.word_size - self.current_location % self.word_size

    def Pass(self, lines):
        self.current_location = 64
        for line in lines:
            # loại bỏ chú thích
            if '#' in line:
                line = line[0:line.find('#')].rstrip()

            if len(line) <= 1:
                continue
            #lưu vào list labels và loại bỏ label
            if ':' in line:
                label = line[0:line.find(':')]
                self.symbol_table[label] = str(self.current_location)
                line = line[line.find(':') + 1:].strip()
            args=re.split('[, ]+', line.rstrip())
            instruction = args[0]
            # Phan tich lenh thanh ma may
            if instruction in self.instruction_table.keys():

                self.parse_instruction(instruction,args)
            # tăng địa chỉ để thực hiện câu lệnh tiếp theo
            self.current_location += self.word_size
            # in ra mã máy của tập lệnh
        self.output_machinecode()
    def parse_instruction(self, instruction,raw_args):
        # lấy core instruction format của lệnh
        list_field=self.instruction_table[instruction]
        arg_count = 0
        offset = 'not_valid'
        args = raw_args[:]
        if '(' in args[2]:
            offset = int(args[2][0:args[2].find('(')])
            args[2] = args[2][args[2].find('(') + 1: args[1].find(')')]
            # chuyển offset sang binary
            if offset < 0:
                offset = bin((1 << 12) + offset)[2:]
            else:
                offset = bin(offset)[2:].zfill(12)

            if 's' in instruction: #S-type
                list_field[2] = bin(self.register_table[args[2]])[2:].zfill(5)
                list_field[1] = bin(self.register_table[args[1]])[2:].zfill(5)
                list_field[0] = offset[0:7]
                list_field[4] = offset[7:]
            # đổi lệnh sang mã máy
            else: #I-type đối với các lệnh load
                list_field[3] = bin(self.register_table[args[1]])[2:].zfill(5)
                list_field[1] = bin(self.register_table[args[2]])[2:].zfill(5)
                list_field[0] = offset

            list_machinecode = self.sumallmachinde_code(list_field)
            self.output_array.append(list_machinecode)
            return
        elif  '0110011' in list_field:  #R-type
            list_field[1] = bin(self.register_table[args[3]])[2:].zfill(5)
            list_field[2] = bin(self.register_table[args[2]])[2:].zfill(5)
            list_field[4] = bin(self.register_table[args[1]])[2:].zfill(5)
            list_machinecode=self.sumallmachinde_code(list_field)
            self.output_array.append(list_machinecode)
            return
        elif len(list_field) == 5:  #I-type
            # trường hợp imm là số hex
            if 'x' in args[3]:
                offset = args[3][args[3].find('x') + 1:]
                offset = bin(int(offset, 16))[2:].zfill(12)
            # phân tích imm là decimal
            else :
                if int(args[3]) < 0:
                    offset = bin((1 << 12) + int(args[3]))[2:]
                else:
                    offset = bin(int(args[3]))[2:].zfill(12)
                # sử lí các lệnh có offset đặt biệt của i type.
                if instruction == 'slli' or instruction == 'srli':
                    offset = '0000000' + offset[7:]
                elif instruction == 'srai':
                    offset = '0100000' + offset[7:]
            # gán giá trị vào core instruction format
            list_field[0] = offset
            list_field[1] = bin(self.register_table[args[2]])[2:].zfill(5)
            list_field[3] = bin(self.register_table[args[1]])[2:].zfill(5)
            # đổi lệnh sang mã máy
            list_machinecode = self.sumallmachinde_code(list_field)
            self.output_array.append(list_machinecode)
            return
        elif '1100011' in list_field:
            offset = self.symbol_table[args[3]] - self.current_location
            if offset < 0:
                offset = bin((1 << 13) + offset)[2:]
            else:
                offset = bin(offset)[2:].zfill(13)

            # chuyển thanh ghi sang số nhị phân
            register_1 = bin(self.register_table[args[1]])[2:].zfill(5)
            register_2 = bin(self.register_table[args[2]])[2:].zfill(5)
            # gán giá trị vào core instruction forma
            list_field[0] = offset[0] + offset[2:8]
            list_field[1] = register_2
            list_field[2] = register_1
            list_field[4] = offset[8:12] + offset[1]

            # tính mã máy của lệnh
            list_machinecode = self.sumallmachinde_code(list_field)
            self.output_array.append(list_machinecode)
            return
        elif args[2] not in self.register_table.keys(): #U-type and J-type
            if 'j' in instruction:
                # phân tích offset nếu imm là một lable
                if args[2] in self.symbol_table.keys():
                    offset = self.symbol_table[args[2]] - self.current_location
                    if offset < 0:
                        offset = bin((1 << 21) + offset)[2:]
                    else:
                        offset = bin(offset)[2:].zfill(21)
                # gán offet vào core instruction format
                list_field[0] = offset[0] + offset[10:20] + offset[9] + offset[1:9]
            else:
                # phân tích offset nếu imm là số hex
                if 'x' in args[1]:
                    offset = args[2][args[2].find('x') + 1:]
                    offset = bin(int(offset, 16))[2:].zfill(20)
                # phân tích offset nếu imm là số dec
                else:
                    if int(args[2]) < 0:
                        offset = bin((1 << 20) + int(args[1]))[2:].zfill(20)
                    else:
                        offset = bin(int(args[1]))[2:].zfill(20)
                # gán offet vào core instruction format
                list_field[0] = offset
            # gán giá trị vào core instruction format còn lại
            list_field[1] = bin(self.register_table[args[1]])[2:].zfill(5)
            list_machinecode = self.sumallmachinde_code(list_field)
            self.output_array.append(list_machinecode)
            return

    def sumallmachinde_code(self,list_machinecode):
        machine_code = ''
        for element in list_machinecode:
            machine_code+=element
        return machine_code

    def output_machinecode(self):
        for x in self.output_array:
            print(x)
