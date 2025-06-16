import React, { useRef, useEffect } from "react";
import ForceGraph2D from "react-force-graph-2d";

export default function SimilaridadGraph({ data = { nodes: [], links: [] }, filters = {} }) {
  const fgRef = useRef();

  // Seguridad: asegurar que data.nodes y data.links existan
  const nodes = Array.isArray(data.nodes) ? data.nodes : [];
  const links = Array.isArray(data.links) ? data.links : [];

  // Filtro defensivo de nodos
  const filteredNodes = nodes.filter((n) => {
    if (!n) return false;
    return (
      (!filters.carrera || n.carrera === filters.carrera) &&
      (!filters.area || n.area === filters.area)
    );
  });

  // Solo mantener enlaces que conectan nodos válidos
  const filteredLinks = links.filter((l) => {
    const sourceExists = filteredNodes.some(n => n.id === l.source);
    const targetExists = filteredNodes.some(n => n.id === l.target);
    return sourceExists && targetExists;
  });

  const nodeColor = (node) => {
    switch (node?.area) {
      case "Matemáticas": return "blue";
      case "Programación": return "green";
      case "Ciencias Sociales": return "red";
      default: return "gray";
    }
  };

  const nodeLabel = (node) =>
    node?.id ? `${node.id} (${node.carrera ?? "?"})` : "";

  console.log("📊 Renderizando grafo con nodos:", filteredNodes);

  return (
    <div style={{ height: "600px", border: "1px solid #ccc" }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={{ nodes: filteredNodes, links: filteredLinks }}
        nodeLabel={nodeLabel}
        nodeAutoColorBy="area"
        linkDirectionalArrowLength={5}
        linkDirectionalArrowRelPos={0.9}
        nodeCanvasObjectMode={() => "after"}
        nodeCanvasObject={(node, ctx, globalScale) => {
          if (!node?.id) return;
          const label = node.id;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = "black";
          ctx.fillText(label, node.x + 6, node.y + 6);
        }}
      />
    </div>
  );
}
