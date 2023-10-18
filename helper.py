# convert opcode from dbus array of bytes to integer 
def bytes_to_int(bytes_arr):
    int_in_bytes = [bytes([b]) for b in bytes_arr]
    return int.from_bytes(int_in_bytes[0] + int_in_bytes[1], 'little')

# converts an integer to a size-bit binary string
def int_to_bits(num, size):
    return bin(num)[2:].zfill(size)
