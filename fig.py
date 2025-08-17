import pandas as pd
import re
from pyvis.network import Network
import matplotlib.colors as mcolors
import matplotlib as plt
import json

# Função para limpar relacionamentos (remove conteúdo entre parênteses)
def clean_relationship(text):
    if pd.isna(text):
        return []
    # Remove tudo entre parênteses e espaços extras
    cleaned = re.sub(r'\([^)]*\)', '', str(text)).strip()
    # Separa por vírgula e remove strings vazias
    return [item.strip() for item in cleaned.split(',') if item.strip()]

# Carregar os CSVs
df_knowledge = pd.read_csv("Knowledge & Skills.csv")
df_blocks = pd.read_csv("Knowledge Blocks.csv")
df_projects = pd.read_csv("Projects.csv")

# Dicionário para mapear nomes de nós a IDs únicos (evitar duplicatas)
node_ids = {}
nodes = []
edges = []

# Gere cores automaticamente para valores únicos de 'Source'
unique_sources = df_projects['Source'].unique()
color_map = {source: mcolors.to_hex(plt.cm.tab20(i)) for i, source in enumerate(unique_sources)}

# Adicionar nós e arestas para cada tabela
def process_table(df, table_name):
    # Conjunto para armazenar pares de nós já conectados
    existing_edges = set()

    for _, row in df.iterrows():
        node_name = str(row['Name']).strip()
        
        # Cria o nó se não existir (mantendo todo o código original)
        if node_name not in node_ids:
            node_id = len(node_ids)
            node_ids[node_name] = node_id
            
            node_data = {
                "id": node_id,
                "label": node_name,
                "group": table_name
            }

            # Tooltips específicos por tabela
            if table_name == "Projects":
                tooltip = f"""
                        <div style='text-align: left; padding: 5px'>
                            <div style='font-weight: bold; margin-bottom: 5px; color: {node_data.get("color", "#000")}'>{node_name}</div>
                            <div><span style='font-weight: bold'>Source:</span> {row.get('Source', 'N/A')}</div>
                            <div><span style='font-weight: bold'>Knowledge Blocks:</span> {row.get('Knowledge Blocks', 'N/A')}</div>
                            <div><span style='font-weight: bold'>Knowledge & Skills:</span> {row.get('Knowledge & Skills', 'N/A')}</div>
                            <div><span style='font-weight: bold'>Projects:</span> {row.get('Projects', 'N/A')}</div>
                            <div><span style='font-weight: bold'>Quests:</span> {row.get('Quests', 'N/A')}</div>
                        </div>
                        """
                node_data["title"] = tooltip
                
                # Adiciona cor baseada na Source
                if 'Source' in row and pd.notna(row['Source']):
                    source = row['Source']
                    if source in color_map:
                        node_data["color"] = color_map[source]
                        node_data["borderWidth"] = 2  # Borda mais destacada

            elif table_name == "Knowledge Blocks":
                tooltip = f"""
                            <div style='text-align: left; padding: 5px'>
                                <div style='font-weight: bold; margin-bottom: 5px; color: #2B7CE9'>{node_name}</div>
                                <div><span style='font-weight: bold'>Knowledge & Skills:</span> {row.get('Knowledge & Skills', 'N/A')}</div>
                                <div><span style='font-weight: bold'>Projects:</span> {row.get('Projects', 'N/A')}</div>
                            </div>
                            """
                node_data["title"] = tooltip
                node_data["color"] = "#D2E5FF"  # Cor padrão para Knowledge Blocks

            elif table_name == "Knowledge & Skills":
                tooltip = f"""
                        <div style='text-align: left; padding: 5px'>
                            <div style='font-weight: bold; margin-bottom: 5px; color: #FFA500'>{node_name}</div>
                            <div><span style='font-weight: bold'>Sources:</span> {row.get('Sources', 'N/A')}</div>
                            <div><span style='font-weight: bold'>Types:</span> {row.get('Types', 'N/A')}</div>
                            <div><span style='font-weight: bold'>Knowledge Blocks:</span> {row.get('Knowledge Blocks', 'N/A')}</div>
                            <div><span style='font-weight: bold'>Projects:</span> {row.get('Projects', 'N/A')}</div>
                        </div>
                        """
                node_data["title"] = tooltip
                node_data["color"] = "#FFD2D2"  # Cor padrão para Knowledge & Skills

            nodes.append(node_data)
        
        current_id = node_ids[node_name]
        
        # Processamento de relacionamentos com verificação de duplicatas
        if table_name == "Knowledge & Skills":
            relation_cols = ["Knowledge Blocks", "Projects"]
            for col in relation_cols:
                if col in df.columns:
                    for related in clean_relationship(row.get(col, "")):
                        related = str(related).strip()
                        if related in node_ids:
                            edge_pair = tuple(sorted((current_id, node_ids[related])))
                            if edge_pair not in existing_edges:
                                edges.append({"from": current_id, "to": node_ids[related]})
                                existing_edges.add(edge_pair)

        elif table_name == "Knowledge Blocks":
            relation_cols = ["Knowledge & Skills", "Projects"]
            for col in relation_cols:
                if col in df.columns:
                    for related in clean_relationship(row.get(col, "")):
                        related = str(related).strip()
                        if related in node_ids and related != node_name:
                            edge_pair = tuple(sorted((current_id, node_ids[related])))
                            if edge_pair not in existing_edges:
                                edges.append({"from": current_id, "to": node_ids[related]})
                                existing_edges.add(edge_pair)

        elif table_name == "Projects":
            relation_cols = ["Knowledge Blocks", "Knowledge & Skills", "Projects"]
            for col in relation_cols:
                if col in df.columns:
                    for related in clean_relationship(row.get(col, "")):
                        related = str(related).strip()
                        if related in node_ids and related != node_name:
                            edge_pair = tuple(sorted((current_id, node_ids[related])))
                            if edge_pair not in existing_edges:
                                edges.append({"from": current_id, "to": node_ids[related]})
                                # Para relacionamentos entre Projects, cria apenas uma aresta
                                if col != "Projects":
                                    existing_edges.add(edge_pair)

# Processar todas as tabelas
process_table(df_knowledge, "Knowledge & Skills")
process_table(df_blocks, "Knowledge Blocks")
process_table(df_projects, "Projects")

# [Todo o código anterior até a criação da rede permanece igual]

# Configuração da rede
net = Network(
    height="800px", 
    width="100%", 
    notebook=False,
    directed=True,
    cdn_resources='in_line'
)

# Primeiro: Mostrar botões de controle (ANTES de set_options)
net.show_buttons(filter_=['physics', 'nodes', 'edges'])

import random
# Definir zonas para cada grupo
GROUP_ZONES = {
    "Projects": {
        "x_range": (-1500, -400),  # Esquerda
        "y_range": (1400, 0)      # Inferior
    },
    "Knowledge Blocks": {
        "x_range": (400, 1500),    # Direita 
        "y_range": (1400, 0)      # Inferior
    },
    "Knowledge & Skills": {
        "x_range": (-700, 700),   # Centro
        "y_range": (-400, -1500)     # Superior
    }
}

# Atribuir posições fixas
for group_name, zone in GROUP_ZONES.items():
    # Filtrar nós deste grupo
    group_nodes = [n for n in nodes if n["group"] == group_name]
    
    if not group_nodes:
        continue
    
    # Identificar cores únicas neste grupo
    unique_colors = set()
    for node in group_nodes:
        if "color" in node:
            unique_colors.add(node["color"])
    
    num_colors = max(1, len(unique_colors))  # Pelo menos 1 se não houver cores definidas
    
    # Dividir o intervalo Y em partes iguais
    y_min, y_max = zone["y_range"]
    y_range_total = y_max - y_min
    y_section_height = y_range_total / num_colors
    
    # Criar um mapeamento de cor para sub-intervalo Y
    color_to_y_range = {}
    for i, color in enumerate(sorted(unique_colors)):
        color_y_min = y_min + i * y_section_height
        color_y_max = color_y_min + y_section_height
        color_to_y_range[color] = (color_y_min, color_y_max)
    
    # Se não houver cores, usar o intervalo completo
    if not color_to_y_range:
        color_to_y_range[None] = (y_min, y_max)
    
    # Distribuir os nós
    for node in group_nodes:
        node_color = node.get("color")
        y_range = color_to_y_range.get(node_color, (y_min, y_max))
        
        node["x"] = random.uniform(*zone["x_range"])
        node["y"] = random.uniform(*y_range)

# Adicionar nós
for node in nodes:
    net.add_node(
        node["id"],
        label=node["label"],
        group=node["group"],
        title=node.get("title", ""),
        color=node.get("color"),
        x=node.get("x", None),
        y=node.get("y", None),
        borderWidth=node.get("borderWidth", 1)
    )

# Adicionar arestas
for edge in edges:
    net.add_edge(edge["from"], edge["to"])

# Configuração visual final
options = {
    "nodes": {
        "shape": "dot",
        "font": {
            "size": 12,
            "color": "rgba(0,0,0,1)",
            "strokeWidth": 0,
            "align": "center",
            "vadjust": 35
        },
        "borderWidth": 1,
        "shadow": True
    },
    "edges": {
        "smooth": {
            "type": "continuous",
            "roundness": 0.2
        }
    },
    "interaction": {
        "tooltipDelay": 0,
        "hover": True,
        "hideEdgesOnDrag": True,
        "tooltip": {
            "useHtml": True,
            "cssClass": "custom-tooltip"
        }
    }
}

net.set_options(json.dumps(options))




# ... (mantenha todo o código anterior até a geração do HTML)
import re
for n in nodes:
    if 'title' in n:
        n['title'] = re.sub(r'\([^)]*\)', '', n['title'])

# Depois continue com a geração do HTML como antes
nodes_json = json.dumps([{
    "id": n["id"],
    "label": n["label"],
    "title": n.get("title", "").strip(),
    "group": n["group"],
    "color": n.get("color", "#97C2FC"),
    "shape": "dot",
    "x": n.get("x", 0),
    "y": n.get("y", 0),
    "physics": True,
    "font": {"size": 12, "vadjust": 35}
} for n in nodes], ensure_ascii=False)
# Classe personalizada para serialização JSON que preserva HTML
class HTMLUnescapedEncoder(json.JSONEncoder):
    def encode(self, obj):
        # Primeiro faz a serialização padrão
        json_str = super().encode(obj)
        # Depois remove o escaping das tags HTML
        json_str = json_str.replace('\\"', '"')
        json_str = json_str.replace('\\n', '\n')
        json_str = json_str.replace('\\t', '\t')
        return json_str

with open("index.html", "w", encoding="utf-8") as f:
    # Template com tratamento unificado para hover e click
    html_template = """<!DOCTYPE html>
<html>
<head>
  <title>Knowledge Graph</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    #network {{
      width: 100%;
      height: 100vh;
      border: 1px solid #ccc;
    }}
    .custom-tooltip {{
      position: absolute;
      max-width: 300px;
      padding: 8px;
      background: white;
      border: 1px solid #ccc;
      border-radius: 3px;
      pointer-events: none;
      font-family: Arial;
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
      z-index: 100;
      display: none;
      font-size: 12px !important; 
    }}
    .custom-tooltip div {{
      margin: 3px 0;
    }}
  </style>
</head>
<body>
  <div id="network"></div>
  <div id="tooltip" class="custom-tooltip"></div>
  
  <script>
    // Processa os dados para garantir HTML válido
    function processTooltip(html) {{
      if (!html) return '';
      // Cria um elemento temporário para converter texto em HTML
      var temp = document.createElement('div');
      temp.innerHTML = html.trim();
      return temp.innerHTML;
    }}

    // Dados dos nós com tooltips processados
    var nodesData = {nodes_data};
    var edgesData = {edges_data};
    
    var nodes = new vis.DataSet(nodesData.map(function(node) {{
      return {{
        id: node.id,
        label: node.label,
        group: node.group,
        color: node.color,
        shape: node.shape,
        x: node.x,
        y: node.y,
        font: node.font,
        // Armazena o HTML original como atributo
        rawTitle: node.title
      }};
    }}));
    
    var edges = new vis.DataSet(edgesData);
    
    var container = document.getElementById('network');
    var tooltip = document.getElementById('tooltip');
    
    var options = {{
      nodes: {{
        font: {{ size: 12, vadjust: 35 }}
      }},
      interaction: {{
        hover: true,
        tooltipDelay: 0,
        hideEdgesOnDrag: true
      }},
      physics:{{ 
        enabled: false // Deve ser false para manter as posições fixas
    }}
    }};
    
    var network = new vis.Network(container, {{nodes: nodes, edges: edges}}, options);
    
    // Tratamento unificado para hover e click
    network.on("hoverNode", function(params) {{
      if (params.node) {{
        var node = nodes.get(params.node);
        tooltip.innerHTML = processTooltip(node.rawTitle);
        tooltip.style.display = 'block';
        tooltip.style.left = params.pointer.DOM.x + 'px';
        tooltip.style.top = params.pointer.DOM.y + 'px';
      }}
    }});
    
    network.on("blurNode", function() {{
      tooltip.style.display = 'none';
    }});
    
    network.on("click", function(params) {{
      if (params.nodes.length > 0) {{
        var node = nodes.get(params.nodes[0]);
        tooltip.innerHTML = processTooltip(node.rawTitle);
        tooltip.style.display = 'block';
        tooltip.style.left = params.pointer.DOM.x + 'px';
        tooltip.style.top = params.pointer.DOM.y + 'px';
      }} else {{
        tooltip.style.display = 'none';
      }}
    }});
    
    // Esconde o tooltip ao mover o mouse
    container.addEventListener('mousemove', function() {{
      tooltip.style.display = 'none';
    }});
  </script>
</body>
</html>"""

    # Prepara os dados para substituição
    nodes_data = json.dumps([{
        "id": n["id"],
        "label": n["label"],
        "title": n.get("title", ""),
        "group": n["group"],
        "color": n.get("color", "#97C2FC"),
        "shape": "dot",
        "x": n.get("x", 0),
        "y": n.get("y", 0),
        "physics": True,
        "font": {"size": 12, "vadjust": 35}
    } for n in nodes], ensure_ascii=False)

    edges_data = json.dumps(edges, ensure_ascii=False)

    # Substitui os placeholders usando format()
    html_content = html_template.format(
        nodes_data=nodes_data,
        edges_data=edges_data
    )
    f.write(html_content)