# fix_indentation.py
import os

def fix_file_indentation(filepath):
    """Corrigir indentação de um arquivo"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        # Remover espaços em branco no início e fim
        stripped = line.strip()
        if stripped:
            # Adicionar com indentação padrão de 4 espaços
            fixed_lines.append('    ' + stripped + '\n')
        else:
            fixed_lines.append('\n')
    
    # Escrever arquivo corrigido
    with open(filepath, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Arquivo {filepath} corrigido!")

# Corrigir o arquivo problemático
fix_file_indentation('trader/bybit_analyser.py')
