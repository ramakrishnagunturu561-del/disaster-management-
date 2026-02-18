import { useState, useCallback } from 'react';
import type { DamageDetection, BoundingBox } from '@/types';

// Simulate damage detection analysis
const analyzeImage = (imageUrl: string): Promise<DamageDetection> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Generate random bounding boxes for demo
      const numBoxes = Math.floor(Math.random() * 5) + 3;
      const boundingBoxes: BoundingBox[] = [];
      
      for (let i = 0; i < numBoxes; i++) {
        boundingBoxes.push({
          x: Math.random() * 300 + 50,
          y: Math.random() * 200 + 50,
          width: Math.random() * 100 + 50,
          height: Math.random() * 80 + 40,
          label: ['Building Damage', 'Debris', 'Structural Collapse', 'Fire'][Math.floor(Math.random() * 4)],
          confidence: Math.random() * 0.3 + 0.7,
        });
      }

      // Generate heatmap data
      const heatmapData: number[][] = [];
      for (let i = 0; i < 50; i++) {
        const row: number[] = [];
        for (let j = 0; j < 50; j++) {
          row.push(Math.random() * (boundingBoxes.some(b => 
            j * 8 >= b.x && j * 8 <= b.x + b.width &&
            i * 6 >= b.y && i * 6 <= b.y + b.height
          ) ? 0.9 : 0.1));
        }
        heatmapData.push(row);
      }

      const damageScore = Math.floor(Math.random() * 40) + 60;
      
      resolve({
        id: `det-${Date.now()}`,
        imageUrl,
        boundingBoxes,
        heatmapData,
        damageScore,
        confidence: Math.random() * 0.2 + 0.8,
        explanation: generateExplanation(damageScore, boundingBoxes),
        timestamp: new Date(),
      });
    }, 2000);
  });
};

const generateExplanation = (damageScore: number, boxes: BoundingBox[]): string => {
  const damageTypes = [...new Set(boxes.map(b => b.label))];
  return `AI Analysis detected ${boxes.length} damaged regions with ${damageScore}% overall severity. ` +
    `Primary damage types: ${damageTypes.join(', ')}. ` +
    `Highest confidence detection: ${boxes.sort((a, b) => b.confidence - a.confidence)[0]?.label} ` +
    `(${Math.round(boxes[0]?.confidence * 100)}% confidence). ` +
    `Recommendation: ${damageScore > 70 ? 'Immediate structural assessment required.' : 'Standard damage assessment protocol.'}`;
};

export function useDamageDetection() {
  const [detections, setDetections] = useState<DamageDetection[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentDetection, setCurrentDetection] = useState<DamageDetection | null>(null);

  const uploadAndAnalyze = useCallback(async (file: File) => {
    setIsAnalyzing(true);
    
    try {
      // Create object URL for the uploaded image
      const imageUrl = URL.createObjectURL(file);
      
      // Simulate AI analysis
      const detection = await analyzeImage(imageUrl);
      
      setDetections(prev => [detection, ...prev]);
      setCurrentDetection(detection);
      
      return detection;
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const selectDetection = useCallback((id: string) => {
    const detection = detections.find(d => d.id === id);
    setCurrentDetection(detection || null);
  }, [detections]);

  const clearDetections = useCallback(() => {
    setDetections([]);
    setCurrentDetection(null);
  }, []);

  return {
    detections,
    currentDetection,
    isAnalyzing,
    uploadAndAnalyze,
    selectDetection,
    clearDetections,
  };
}
