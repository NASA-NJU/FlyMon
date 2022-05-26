from bitstring import BitArray, BitStream

class FlowKey:
    """Flow key definition"""
    def __init__(self, candidate_key_list):
        """
        Initially are key are not enabled.
        """
        self.key_list = dict(candidate_key_list)
        for key in self.key_list.keys():
            bits = self.key_list[key]
            self.key_list[key] = (bits, BitArray(int=0, length=bits))
    
    def set_mask(self, key_name, mask):
        """
        Set a mask to one of the candidate key.
        """
        if mask[0:2] != "0x":
            print("Invalid mask without leading '0x' or invalid mask length.") 
            return False
        origin_bits, _ = self.key_list[key_name]
        if len(mask[2:]) != origin_bits/4:
            print("Expected length: {}, given: {}.".format(origin_bits), len(mask[2:])*4)
            return False
        self.key_list[key_name] = (origin_bits, BitArray(mask))
        return True

    def reset(self):
        """
        Reset a compressed key.
        """
        for key in self.key_list.keys():
            bits,_ = self.key_list[key]
            self.key_list[key] = (bits, BitArray(int=0, length=bits))

    def to_string(self):
        """
        Formally return a string of the key. Only the enabled key are listed,
        """
        key_string = " - ".join(["{}({})".format(key, self.key_list[key][1]) for key in self.key_list])
        return key_string

    def to_config_dict(self):
        """
        return a list of configs.
        { key_name: [(start bits, length)] }
        """
        config_dict = {}
        for key in self.key_list.keys():
            size, mask = self.key_list[key]
            mask_bitstr = mask.bin
            config_dict[key] = [] # each key may contains multiple inner-tupples.
            ptr = 0
            status = 0 # finding(0), calculating(1), storing(2)
            start_bit = 0
            length = 0
            while ptr != size:
                bit = mask_bitstr[ptr]
                if status == 0: # finding status.
                    if bit == '0':
                        pass
                    else:
                        status = 1
                        start_bit = ptr
                        length += 1
                    ptr += 1
                if status == 1: # getting a 1
                    if bit == '0':
                        status = 2 
                    else:
                        length += 1
                        ptr += 1
                if status == 2:
                    config_dict[key].append((start_bit, length))
                    length = 0
                    status = 0
                    ptr += 1
            if status == 1:
                config_dict[key].append((start_bit, length))
        print("DEBUG hash dict: {}".format(str(config_dict)))
        return config_dict
