import json
import os

from ghidra.program.model.block import BasicBlockModel

try:
    from ghidra.ghidra_builtins import *
except:
    pass

# This script is meant to dump rust funcs
# Prerequisites:
#   1. ghidra version: 10.1
#   2. rustc version: https://github.com/pkuGenuine/rust/commit/a2ecbf87cf355a121a62f0629ea5f880c9bf41fc
#   3. platform: amd64/Ubuntu20.04
#   4. DO NOT contain DWARF info when analysing via ghidra, other wise 
#       func.toString() won't return origin func label, which starts
#       with '_Z' or '_R'


def get_funcs():
    """Initialize all functions as a list of funcs

    :return: a list of funcs
    """
    func_list = []

    func_db = currentProgram.getFunctionManager()
    func_iter = func_db.getFunctions(True)
    while func_iter.hasNext():
        current_func = func_iter.next()
        func_list.append(current_func)
    return func_list


def get_bbs(func_body):
    """Collect basic blocks from the function body and convert them into a list

    :param func_body: func.body
    :return: a list of basic blocks
    """
    block_model_iterator = BasicBlockModel(currentProgram)
    b_iter = block_model_iterator.getCodeBlocksContaining(func_body, monitor)

    blocks = []
    while b_iter.hasNext():
        block = b_iter.next()
        blocks.append(block)

    return blocks


def get_instructions(bb):
    """Get instructions of a basic block

    :param bb: basic block
    :return: a list of instruction
    """
    ret = []
    start_addr, end_addr = bb.getMinAddress(), bb.getMaxAddress()
    ins = getInstructionAt(start_addr)
    while ins and (start_addr <= ins.getAddress() <= end_addr):
        ret.append(ins.toString())
        # The problem is, when ghidra fails to disasm the bytes right
        #   behind, the method returns the next disasmed instruction.
        #   Even though current instruct will not to drop to that one.
        ins = ins.getNext()
    return ret


def get_sig(func):
    """Generate signature for a function.
    The signature is a coarse implementation of IDA FLIRT

    :param func: function
    :type func: str
    """

    def u32(byte_array, little_endding):
        assert len(byte_array) == 4
        if not little_endding:
            raise NotImplementedError
        ret = 0
        for i in range(4):
            ret += (0x100 ** i) * \
                (byte_array[i] if byte_array[i] >= 0 else byte_array[i] + 256)
        if ret >= 0xf0000000:
            ret -= 0x100000000
        return ret

    start_addr = func.getEntryPoint()
    addr_lim = min(func.getBody().getMaxAddress().add(1), start_addr.add(0x20))
    instruction = getInstructionAt(start_addr)
    sig = ''
    while instruction and instruction.address < addr_lim:
        valid_ref = False
        raw_bytes = instruction.getBytes()
        call_refs = list(filter(lambda r: r.getReferenceType().isCall(
        ) and r.getReferenceType().isUnConditional(), instruction.referencesFrom))
        data_refs = list(filter(lambda r: r.getReferenceType().isData() and not r.isStackReference(
        ), instruction.referencesFrom))
        refs = data_refs + call_refs
        # Call handle most of situation for amd64
        # It is possible to recognize '\xe8' ( call ), '\xe9' ( jmp ), etc.
        #   to make it more precise
        if len(refs) == 1 and len(raw_bytes) >= 5:
            r = refs[0]
            to_addr = r.toAddress
            # Do not use instruction.next, in case the bytes after current
            #   instruction is not disasmed.
            next_addr = instruction.address.add(len(raw_bytes))
            possible_offset = raw_bytes[-4:]
            possible_opcode = raw_bytes[:-4]
            if len(possible_opcode) > 0 and next_addr.add(u32(possible_offset, little_endding=True)) == to_addr:
                sig += ''.join([hex(b if b >= 0 else b + 256)
                               [2:].rjust(2, '0') for b in possible_opcode])
                sig += '..' * 4
                valid_ref = True
        if not valid_ref:
            sig += ''.join([hex(b if b >= 0 else b + 256)
                           [2:].rjust(2, '0') for b in raw_bytes])
        instruction = instruction.next
    return sig[:0x40].ljust(0x40, '-')


def get_cfg(func):
    """Get cfg of a function.
    The cfg is represented as a list of edges.
    edge: (s, d, type)
    type: 0/1 (unconditional/conditional)

    :param func: function
    :return: list of edges
    """
    body = func.getBody()
    blocks = get_bbs(body)
    edges = []
    for block in blocks:
        base_id = blocks.index(block)
        des_iter = block.getDestinations(monitor)
        while des_iter.hasNext():
            des = des_iter.next()
            des_type = des.flowType

            if des.getDestinationBlock() in blocks:
                target_id = blocks.index(des.getDestinationBlock())
                edge_type = 0 if des_type is not des_type.CONDITIONAL_JUMP else 1
                edges.append((base_id, target_id, edge_type))
    return edges


def get_bbs_info(func):
    """Get instruction list for each bb of a function

    :param func: function
    :return: dict, map block id to its instructions
    """
    body = func.getBody()
    blocks = get_bbs(body)
    return {blocks.index(block): get_instructions(block) for block in blocks}


if __name__ == '__main__':
    # TODO: ChangeMe
    base_dir = ''
    # Sometimes getProgramFile is not available, change it manually
    file_name = getProgramFile().getName()
    func_list = get_funcs()
    func_info_dict = {}

    for func in func_list:
        func_name = func.toString()
        entry_point = func.getEntryPoint()
        is_rust_func = func_name[:2] in ['_Z', '_R']
        func_info_dict[entry_point.toString()] = {
            'func_name': func_name,
            'is_rust_func': is_rust_func,
            'edges': get_cfg(func),
            'bbs': get_bbs_info(func),
            'sig': get_sig(func) if is_rust_func else ''
        }

    with open(os.path.join(base_dir, file_name + '.json'), 'w') as f:
        json.dump(func_info_dict, f, indent=2)
