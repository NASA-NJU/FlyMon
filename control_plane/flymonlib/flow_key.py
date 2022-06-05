import socket

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

    def generate_bytes(self, key_str):
        """Generate bytes according to the key template.
        Args:
            key_str : '10.0.0.0,20.0.0.1,...'
        Returns:
            bytes
        """
        try:
            keys = key_str.split(',')
            for key in keys:
                name, value = key.split('=')
                bits, prefix = self.key_list[key_name]
                if prefix == 0:
                    continue
                query_key = keys.pop(0)
                if prefix == bits:
                    query_key = query_key.split('/')[0]
                else:
                    query_key, query_prefix = query_key.split('/')
                
            socket.inet_aton('164.107.113.18')

        except Exception as e:
            print(f"Error when parse the query ket string {key_str}")
            return None

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
        for key in self.key_list.keys():
            _, prefix = self.key_list[key]
            config_dict[key] = [] # each key may contains multiple inner-tupples.
            config_dict[key].append((0, prefix))
        return config_dict
