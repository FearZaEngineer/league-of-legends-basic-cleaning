import json
import struct
from xxhash import xxh3_64_intdigest, xxh64_intdigest

def key_to_hash(key, bits=40, rsthash_version=1415):
    """Convert a string key to its hash value"""
    if isinstance(key, str):
        if rsthash_version >= 1415:
            key = xxh3_64_intdigest(key.lower())
        else:
            key = xxh64_intdigest(key.lower())
    return key & ((1 << bits) - 1)

# Configuration
input_file = "E:\\lol.stringtable.json"
output_file = "E:\\output.stringtable"
hash_bits = 32
version = 3

# Load JSON
print(f"Loading JSON from {input_file}...")
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"Loaded {len(data)} entries")

# Prepare the entries
entries = {}
for key, value in data.items():
    # Convert non-string values to strings
    if not isinstance(value, str):
        value = json.dumps(value)
        
    if key.startswith('{') and key.endswith('}'):
        # Handle hexadecimal hash format like "{1234abcd}"
        hash_val = int(key[1:-1], 16)
    else:
        # For normal string keys, compute the hash
        hash_val = key_to_hash(key, hash_bits)
    entries[hash_val] = value

# Write RST file
print(f"Writing stringtable to {output_file}...")
with open(output_file, 'wb') as f:
    # Write header
    f.write(b'RST')
    f.write(struct.pack('<B', version))
    
    # Write entries count
    f.write(struct.pack('<L', len(entries)))
    
    # Calculate and write entry references
    hash_mask = (1 << hash_bits) - 1
    offset = 0
    offsets = []
    
    # First pass: collect offsets
    for hash_val in entries:
        packed = (offset << hash_bits) | (hash_val & hash_mask)
        offsets.append(packed)
        offset += len(entries[hash_val].encode('utf-8')) + 1  # +1 for null terminator
    
    # Write offsets
    for packed in offsets:
        f.write(struct.pack('<Q', packed))
    
    # Has TRENC byte (set to 0 for version 3)
    if version < 5:
        f.write(struct.pack('<B', 0))
    
    # Write entries data
    for hash_val, text in entries.items():
        f.write(text.encode('utf-8') + b'\0')

print("Conversion completed!")
