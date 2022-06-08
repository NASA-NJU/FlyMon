class FlowKey:
    """Flow key definition"""
    def __init__(self, candidate_key_list):
        """
        Initially are key are not enabled (the mask is all-0).
        """
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

    def get_bytes_len(self, key_name):
        """
        Get bytes of the key.
        """
        if key_name not in self.key_list:
            raise RuntimeError(f"Invalid Key Name: {key_name}")
        return self.key_list[key_name][0]

    def set(self, another):
        """
        Deep copy.
        """
        for key in another.key_list.keys():
            bits, prefix = another.key_list[key]
            self.key_list[key] = (bits, prefix)
        
    def reset(self):
        """
        Reset a compressed key.
        """
        for key in self.key_list.keys():
            bits,_ = self.key_list[key]
            self.key_list[key] = (bits, 0)

    def __str__(self):
        """
        Formally return a string of the key. Only the enabled key are listed,
        """
        key_string = " - ".join(["{}/{}".format(key, self.key_list[key][1]) for key in self.key_list.keys() if self.key_list[key][1] != 0])
        return key_string
    
    def __eq__(self, __o) -> bool:
        try:
            for key in self.key_list.keys():
                _, prefix = self.key_list[key]
                _, __o_prefix = __o.key_list[key]
                if prefix != __o_prefix:
                    return False
            return True
        except Exception as e:
            print(f"Invalid key: {str(__o)}， caused {str(e)}, when allocate compressed key.")
            return False

    def to_config_dict(self):
        """
        return a list of configs.
        { key_name: [(start bits, length)] }
        """
        config_dict = {}
        for key_name in self.key_list.keys():
            bits, prefix = self.key_list[key_name]
            config_dict[key_name] = []
            # if prefix != 0:
            # how many full bytes does the prefix have
            full_byte_num = prefix // 8
            # how many empty bytes dose the prefix have
            empty_byte_num = (bits-prefix) // 8
            # print(full_byte_num + empty_byte_num, bits // 8)
            if (full_byte_num + empty_byte_num) != bits // 8:
                # where to truncate in the middle byte
                full_lenth = prefix % 8
                config_dict[key_name].append((empty_byte_num*8, full_lenth))
                config_dict[key_name].append((bits - full_byte_num*8, full_byte_num*8))
            else:
                config_dict[key_name].append((bits - full_byte_num*8-1, full_byte_num*8))
            # print(config_dict)
            # else:
            #     config_dict[key_name] = [(bits-1, 0)]
        return config_dict

def parse_key(key_str):
    key_template = {
        "hdr.ipv4.src_addr" : 32,
        "hdr.ipv4.dst_addr" : 32,
        "hdr.ports.src_port": 16,
        "hdr.ports.dst_port": 16,
        "hdr.ipv4.protocol" :  8
    }
    flow_key = FlowKey(key_template)
    try:
        key_list = key_str.split(',')
        for key in key_list:
            if '/' in key:
                k,m = key.split('/')
                if k not in key_template.keys():
                    raise RuntimeError(f"Invalid key format: {key_str}, example: hdr.ipv4.src_addr/<mask:int>, hdr.ports.src_port/<mask:int>")
                if int(m) < 0 or int(m) > key_template[k]:
                    raise RuntimeError(f"Invalid key mask: {m}, need >=0 and <= {key_template[k]}")
                re = flow_key.set_mask(k, int(m))
                if re is False:
                    raise RuntimeError(f"Set mask faild for the key {k}")
            else:
                flow_key.set_mask(key, 32)
    except Exception as e:
        raise e
    return flow_key
