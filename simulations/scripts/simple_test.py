import bin.tester
import time

TEST_DIR_BASE = 'test/'

def logtime():
    return time.strftime("%m_%d_%H_%M", time.localtime())

def test_flow_cardinality_simple():
    test_dir = TEST_DIR_BASE + 'TBC_CARDINALITY/'
    test_file = 'test_tbc_cardinality.cpp_template'
    out_file = 'logs/simple_test_'+logtime()+'.log'
    test_once = bin.tester.Tester(test_dir, test_file, {}, out_file)
    test_once.runTest()
    print("Done.")

if __name__ == "__main__":
    test_flow_cardinality_simple()
    
