hex_array = [b'00', b'00', b'32', b'1C', b'17', b'02', b'11', b'00', b'00', b'00', b'00', b'00', b'00', b'00', b'00', b'00', b'00', b'00', b'78']

int_array = [int(x, 16) for x in hex_array]

print(int_array)