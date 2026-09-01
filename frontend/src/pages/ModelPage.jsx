import { useParams, Navigate } from "react-router-dom";
import { models } from "../data/models";
import FractureDetector from "../components/models/FractureDetector";

const modelComponents = {
  "fracture-detection": FractureDetector,
};

export default function ModelPage() {
  const { modelId } = useParams();
  const model = models.find((m) => m.id === modelId);
  const Component = modelComponents[modelId];

  if (!model) return <Navigate to="/" />;

  return Component ? (
    <Component model={model} />
  ) : (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-white text-xl">{model.name} coming soon!</p>
    </div>
  );
}
