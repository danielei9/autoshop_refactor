str = "b'00 00 01'"
byte_list = str.split()

byte1 = int(byte_list[0], 16)
byte2 = int(byte_list[1], 16)
byte3 = int(byte_list[2], 16)

print(byte1, byte2, byte3)