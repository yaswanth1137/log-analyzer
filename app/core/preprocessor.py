import re

def clean_log_text(raw_log: str) -> str:
    """
    Normalizes unstructured console outputs by stripping dynamic run parameters 
    (timestamps, memory hex arrays, tracking hashes) to expose underlying semantic signatures.
    """
    if not raw_log:
        return ""
        
    lines = raw_log.split('\n')
    processed_lines = []
    
    for line in lines:
        # Filter: Only pass lines likely to contain engineering exceptions or warnings
        line_lower = line.lower()
        if not any(k in line_lower for k in ["error", "exception", "failed", "fail", "traceback", "fatal", "exit"]):
            continue
            
        # 1. Strip standard ISO and database timestamps (e.g., 2026-07-05T07:06:53Z)
        line = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(\.\d+)?Z?', '<TIMESTAMP>', line)
        
        # 2. Mask hexadecimal memory locations and pointer targets (e.g., 0x7fff5fbff618)
        line = re.sub(r'0x[0-9a-fA-F]+', '<MEMORY_ADDR>', line)
        
        # 3. Simplify alphanumeric tracking tokens/IDs or long Git commit hashes
        line = re.sub(r'\b[0-9a-f]{7,40}\b', '<HASH_TOKEN>', line)
        
        # 4. Standardize pure numeric values (ports, thread indices, process identifiers)
        line = re.sub(r'\b\d+\b', '<NUM>', line)
        
        processed_lines.append(line.strip().lower())
        
    return " ".join(processed_lines)