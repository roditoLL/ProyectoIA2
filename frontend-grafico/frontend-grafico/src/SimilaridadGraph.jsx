import React, { useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";

export default function SimilaridadGraph({ data = { nodes: [], links: [] } }) {
  const fgRef = useRef();

  const nodes = Array.isArray(data.nodes) ? data.nodes : [];
  const links = Array.isArray(data.links) ? data.links : [];

  // Tooltip con información completa
  const nodeLabel = (node) => {
    return `
ID: ${node.id}
Nombre: ${node.nombre ?? "?"}
Carrera: ${node.carrera ?? "?"}
Área: ${node.area ?? "?"}
Similitud: ${node.similitud}
    `.trim();
  };

  return (
    <div style={{ height: "600px", border: "1px solid #ccc" }}>
      <ForceGraph2D
        ref={fgRef}
        graphData={{ nodes, links }}
        nodeLabel={nodeLabel}
        nodeAutoColorBy="area"
        linkDirectionalArrowLength={5}
        linkDirectionalArrowRelPos={0.9}
        nodeCanvasObjectMode={() => "after"}
        nodeCanvasObject={(node, ctx, globalScale) => {
          if (!node?.id) return;

          const label = `${node.nombre ?? node.id}`;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = "black";
          ctx.fillText(label, node.x + 6, node.y + 6);
        }}
      />
    </div>
  );
}
