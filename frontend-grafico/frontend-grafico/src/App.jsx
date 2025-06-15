import { useEffect, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";

const SimilaridadGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  useEffect(() => {
    fetch("http://localhost:8000/similares")
      .then((res) => res.json())
      .then((data) => setGraphData(data));
  }, []);

  return (
  <ForceGraph2D
  graphData={graphData}
  nodeLabel={(node) => `${node.id}\nCarrera: ${node.carrera}\nÁrea: ${node.area}`}
  nodeAutoColorBy="area" // color por área
  linkDirectionalArrowLength={4}
  linkDirectionalArrowRelPos={1}
  linkLabel={(link) => `Similitud: ${link.similitud}`}
/>
  );
};

export default SimilaridadGraph;
