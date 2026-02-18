import { useState, useCallback } from 'react';
import { api, type AnalysisResult, type BoundingBox } from '@/services/api';

export interface DetectionResult {
  id: string;
  imageUrl: string;
  boundingBoxes: BoundingBox[];
  heatmapData?: string;
  damageScore: number;
  confidence: number;
  explanation: string;
  timestamp: Date;
}

export function useApiDamageDetection() {
  const [detections, setDetections] = useState<DetectionResult[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentDetection, setCurrentDetection] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uploadAndAnalyze = useCallback(async (file: File, zoneId?: string) => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      // Create object URL for preview
      const imageUrl = URL.createObjectURL(file);
      
      // Call API
      const result = await api.analyzeImage(file, undefined, zoneId);
      
      // Transform to our format
      const detection: DetectionResult = {
        id: result.id,
        imageUrl,
        boundingBoxes: result.bounding_boxes || [],
        heatmapData: result.heatmap_url,
        damageScore: result.results?.damage_score || 0,
        confidence: result.confidence,
        explanation: result.explanation || '',
        timestamp: new Date(result.created_at),
      };
      
      setDetections(prev => [detection, ...prev]);
      setCurrentDetection(detection);
      
      return detection;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setError(message);
      throw err;
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
    setError(null);
  }, []);

  return {
    detections,
    currentDetection,
    isAnalyzing,
    error,
    uploadAndAnalyze,
    selectDetection,
    clearDetections,
  };
}
