#ifndef _P4_H_
#define _P4_H_

#include "HowLog/HowLog.h"
#include "CommonFunc.h"
#include "TracePacket.h"

#include <memory>
#include <string>
#include <map>
#include <vector>
using namespace std;

#define  WILD_CARD  0x1fffffff

class Metadata{
public:
    //必须加虚函数，否则dynamic_pointer_cast会报错.
    virtual ~Metadata(){} 
};


class FlowRuleMatch{
public:
    FlowRuleMatch()=default;
    virtual bool hit(TracePacket* hdr, Metadata* meta)const {};
};


class FlowRuleAction {
public:
    virtual void invoke(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params){};
    virtual ~FlowRuleAction(){};
};



using runnable_action_t = pair<FlowRuleAction*, vector<uint16_t>>;  // action and params

class FlowTable{
public:
    FlowTable(){

    }
    ~FlowTable(){
        for(auto& rule : _rules)
            delete rule.second;
    }
    FlowTable(const FlowTable& ano){
        for(auto& rule : ano._rules){
            FlowRuleAction* new_action = new FlowRuleAction(*(rule.second->first));
            runnable_action_t* new_runnable = new runnable_action_t(make_pair(new_action, rule.second->second));
            _rules.push_back(make_pair(rule.first, new_runnable));
        }
    }
    int addRule(FlowRuleMatch* key, FlowRuleAction* action, const vector<uint16_t>& params){
        runnable_action_t* new_runnable = new runnable_action_t(make_pair(action, params));
        _rules.push_back(make_pair(key,new_runnable));
    }
    int apply(TracePacket* hdr, Metadata* meta){
        for(auto& rule : _rules){
            if(rule.first->hit(hdr, meta)){
                auto& action = rule.second->first;
                auto& params = rule.second->second;
                action->invoke(hdr, meta, params);
                return 0;
            }
        }
        return -1;
    }
private:
    vector<pair<FlowRuleMatch*, runnable_action_t*>> _rules;
};

class FTupleMatch : public FlowRuleMatch{
public:
    FTupleMatch(const string& ipsrc_w_mask,    // 10.0.0.*
                const string& ipdst_w_mask,    // 10.0.0.*
                const string& sport_w_mask,    // uint16_t or *
                const string& dport_w_mask,    // uint16_t or *
                const string& protocol_w_mask) // uint8_t or *
    {
        vector<string> temp_ipsrc;
        vector<string> temp_ipdst;
        Split_String(ipsrc_w_mask,temp_ipsrc,".");
        Split_String(ipdst_w_mask,temp_ipdst,".");
        _src_addr = vector<uint32_t>(4); // 10.0.*.*
        _dst_addr = vector<uint32_t>(4);
        for(auto i=0; i<4; ++i){
            _src_addr[i] = (temp_ipsrc[i] == "*")? WILD_CARD : static_cast<uint32_t>(std::stoul(temp_ipsrc[i]));
            _dst_addr[i] = (temp_ipdst[i] == "*")? WILD_CARD : static_cast<uint32_t>(std::stoul(temp_ipdst[i]));
        }
        _src_port = (sport_w_mask == "*")? WILD_CARD : static_cast<uint32_t>(std::stoul(sport_w_mask)); 
        _dst_port = (dport_w_mask == "*")? WILD_CARD : static_cast<uint32_t>(std::stoul(dport_w_mask)); 
        _protocol = (protocol_w_mask == "*")? WILD_CARD : static_cast<uint32_t>(std::stoul(protocol_w_mask)); 
    }
    FTupleMatch(const FTupleMatch& ano){
        _src_addr = ano._src_addr;
        _dst_addr = ano._dst_addr;
        _src_port = ano._src_port;
        _dst_port = ano._dst_port;
        _protocol = ano._protocol;
    }
    FTupleMatch(const FTupleMatch* ano){
        _src_addr = ano->_src_addr;
        _dst_addr = ano->_dst_addr;
        _src_port = ano->_src_port;
        _dst_port = ano->_dst_port;
        _protocol = ano->_protocol;
    }
    ~FTupleMatch(){
        // empty
    }
    virtual bool hit(TracePacket* hdr, Metadata* meta)const {
        const uint8_t* src_addr = hdr->getSrcBytes();
        const uint8_t* dst_addr = hdr->getDstBytes();
        uint16_t src_port = hdr->getSrcPort();
        uint16_t dst_port = hdr->getDstPort();
        uint8_t protocol = hdr->getProtocol();
        for(auto i=0; i<4; ++i){
            if( _src_addr[i] != WILD_CARD && static_cast<uint32_t>(*(src_addr+i)) != _src_addr[i])
                return false;
            if( _dst_addr[i] != WILD_CARD && static_cast<uint32_t>(*(dst_addr+i)) != _dst_addr[i])
                return false;
        }
        if( _src_port != WILD_CARD && _src_port != static_cast<uint32_t>(src_port))
                return false;
        if( _dst_port != WILD_CARD && _dst_port != static_cast<uint32_t>(dst_port))
                return false;
        if( _protocol != WILD_CARD && _protocol != static_cast<uint32_t>(protocol))
                return false;
        return true;
    }
protected:
    vector<uint32_t>  _src_addr;
    vector<uint32_t>  _dst_addr;
    uint32_t  _src_port;
    uint32_t  _dst_port;
    uint32_t  _protocol;
};

class ActionMaker{
	public:
		static std::atomic<UINT64_T> NEXT_ID;
		/**
		* \copybrief MakeEvent(MEM,OBJ)
		* \tparam MEM \deduced The class method function signature(func).
		* \tparam OBJ \deduced The class type holding the method(object).
		* \tparam T1 \deduced Type of the argument to the underlying function.
		* \param [in] mem_ptr Class method member function pointer
		* \param [in] obj Class instance.
		* \param [in] a1 Argument value to be bound to the underlying function.
		* \returns The constructed EventImpl.
		*/ 
		template <typename MEM, typename OBJ> 
		static FlowRuleAction* make_action(MEM mem_ptr, OBJ obj);
};

template <typename MEM, typename OBJ>
inline FlowRuleAction* ActionMaker::make_action(MEM mem_ptr, OBJ obj){
    class ActionImpl0 : public FlowRuleAction
    {
    public:
        ActionImpl0(OBJ obj, MEM function)
            : _obj(obj),
            _function(function)
            {}
        virtual ~ActionImpl0(){}
    private:
        virtual void invoke(TracePacket* hdr, Metadata* meta, const vector<uint16_t>& params)
        {
            ((*_obj).*_function)(hdr, meta, params); //具体的函数需要的参数.
        }
        OBJ _obj;
        MEM _function;
    };
    return new ActionImpl0(obj, mem_ptr);
}
#endif
