from bitstring import BitArray, BitStream

class FlowKey:
    """Flow key definition"""
    def __init__(self, candidate_key_list):
        """
        Initially are key are not enabled (the mask is all-0).
        """
        # Z it is already a dict ?
        # Z turn entry {key, bits} to {key, (bits, mask)}
        self.key_list = dict(candidate_key_list)
        for key in self.key_list.keys():
            bits = self.key_list[key]
            self.key_list[key] = (bits, 0) # original bits and prefix_mask
    
    def set_mask(self, key_name, key_mask):
        """
        Set a mask to one of the candidate key.
        Input example:
         - key_name : e.g., hdr.ipv4.src_addr
         - key_mask : an integer.
        TODO: current we only support prefix-style masks.
        """
        origin_bits, _ = self.key_list[key_name]
        if key_mask < 0 or key_mask > origin_bits:
            print("Invalid mask length.") 
            return False
        self.key_list[key_name] = (origin_bits, key_mask)
        return True

    def reset(self):
        """
        Reset a compressed key.
        """
        for key in self.key_list.keys():
            bits,_ = self.key_list[key]
            self.key_list[key] = (bits, 0)

    def to_string(self):
        """
        Formally return a string of the key. Only the enabled key are listed,
        """
        key_string = " - ".join(["{}/{}".format(key, self.key_list[key][1]) for key in self.key_list.keys() if self.key_list[key][1] != 0])
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
