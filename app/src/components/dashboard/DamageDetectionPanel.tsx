import { useRef, useState, useCallback } from 'react';
import { Upload, Image as ImageIcon, Brain, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { DamageDetection } from '@/types';

interface DamageDetectionPanelProps {
  detections: DamageDetection[];
  currentDetection: DamageDetection | null;
  isAnalyzing: boolean;
  onUpload: (file: File) => void;
  onSelect: (id: string) => void;
  onClear: () => void;
}

export function DamageDetectionPanel({
  detections,
  currentDetection,
  isAnalyzing,
  onUpload,
  onSelect,
  onClear,
}: DamageDetectionPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  }, [onUpload]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  }, [onUpload]);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-500';
    if (confidence >= 0.7) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <Card className="border-border">
        <CardContent className="p-4">
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              dragActive 
                ? 'border-primary bg-primary/10' 
                : 'border-border hover:border-muted-foreground'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-foreground font-medium">
              Upload satellite or drone imagery
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Drag & drop or click to select
            </p>
            <p className="text-xs text-muted-foreground">
              Supports: JPG, PNG, TIFF (max 100MB)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Progress */}
      {isAnalyzing && (
        <Card className="border-border border-primary/50">
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center animate-pulse">
                <Brain className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">AI Analysis in Progress</p>
                <p className="text-xs text-muted-foreground">Processing image with CV models...</p>
              </div>
            </div>
            <Progress value={45} className="h-2 animate-pulse" />
            <div className="flex justify-between mt-2">
              <span className="text-xs text-muted-foreground">Detecting damage regions...</span>
              <span className="text-xs text-primary">~2 seconds</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Detection */}
      {currentDetection && !isAnalyzing && (
        <Card className="border-border">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Brain className="w-4 h-4 text-primary" />
                AI Analysis Results
              </CardTitle>
              <Button variant="ghost" size="sm" onClick={onClear}>
                <X className="w-4 h-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Image with Overlays */}
            <div className="relative rounded-lg overflow-hidden bg-muted">
              <img
                src={currentDetection.imageUrl}
                alt="Analyzed"
                className="w-full h-48 object-cover"
              />
              
              {/* Bounding Boxes Overlay */}
              <div className="absolute inset-0 pointer-events-none">
                {currentDetection.boundingBoxes.map((box, idx) => (
                  <div
                    key={idx}
                    className="absolute border-2 border-red-500 bg-red-500/20"
                    style={{
                      left: `${(box.x / 400) * 100}%`,
                      top: `${(box.y / 300) * 100}%`,
                      width: `${(box.width / 400) * 100}%`,
                      height: `${(box.height / 300) * 100}%`,
                    }}
                  >
                    <span className="absolute -top-5 left-0 bg-red-500 text-white text-[10px] px-1 rounded">
                      {box.label} {Math.round(box.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>
              
              {/* Heatmap Overlay */}
              <div 
                className="absolute inset-0 opacity-40 mix-blend-overlay pointer-events-none"
                style={{
                  background: `radial-gradient(ellipse at 60% 40%, rgba(239,68,68,0.8) 0%, transparent 50%)`,
                }}
              />
            </div>

            {/* Detection Stats */}
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center p-2 bg-muted rounded-lg">
                <p className="text-xs text-muted-foreground">Damage Score</p>
                <p className={`text-lg font-bold ${
                  currentDetection.damageScore > 70 ? 'text-red-500' :
                  currentDetection.damageScore > 40 ? 'text-yellow-500' :
                  'text-green-500'
                }`}>
                  {currentDetection.damageScore}%
                </p>
              </div>
              <div className="text-center p-2 bg-muted rounded-lg">
                <p className="text-xs text-muted-foreground">Detections</p>
                <p className="text-lg font-bold text-foreground">
                  {currentDetection.boundingBoxes.length}
                </p>
              </div>
              <div className="text-center p-2 bg-muted rounded-lg">
                <p className="text-xs text-muted-foreground">Confidence</p>
                <p className={`text-lg font-bold ${getConfidenceColor(currentDetection.confidence)}`}>
                  {Math.round(currentDetection.confidence * 100)}%
                </p>
              </div>
            </div>

            {/* AI Explanation */}
            <div className="p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Brain className="w-4 h-4 text-primary" />
                <span className="text-xs font-medium text-foreground">AI Explanation</span>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {currentDetection.explanation}
              </p>
            </div>

            {/* Detection List */}
            <div>
              <p className="text-xs font-medium text-foreground mb-2">Detected Damage:</p>
              <div className="space-y-1">
                {currentDetection.boundingBoxes.map((box, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{box.label}</span>
                    <Badge variant="outline" className="text-[10px]">
                      {Math.round(box.confidence * 100)}% confidence
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Previous Detections */}
      {detections.length > 0 && (
        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Previous Analyses ({detections.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[150px]">
              <div className="divide-y divide-border">
                {detections.map(detection => (
                  <div
                    key={detection.id}
                    className={`px-4 py-2 flex items-center gap-3 cursor-pointer hover:bg-muted/50 transition-colors ${
                      currentDetection?.id === detection.id ? 'bg-muted' : ''
                    }`}
                    onClick={() => onSelect(detection.id)}
                  >
                    <ImageIcon className="w-4 h-4 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-foreground truncate">
                        Analysis {detection.id.split('-')[1]}
                      </p>
                      <p className="text-[10px] text-muted-foreground">
                        {detection.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-medium ${
                        detection.damageScore > 70 ? 'text-red-500' :
                        detection.damageScore > 40 ? 'text-yellow-500' :
                        'text-green-500'
                      }`}>
                        {detection.damageScore}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
