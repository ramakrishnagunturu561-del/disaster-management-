import { AlertTriangle, HeartPulse, Shield, TrendingUp, TrendingDown } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Zone } from '@/types';

interface RiskAssessmentPanelProps {
  zones: Zone[];
  selectedZone: string | null;
}

export function RiskAssessmentPanel({ zones, selectedZone }: RiskAssessmentPanelProps) {
  const selectedZoneData = zones.find(z => z.id === selectedZone);
  
  // Calculate overall metrics
  const avgDamage = Math.round(zones.reduce((acc, z) => acc + z.damageScore, 0) / zones.length);
  const avgSurvival = Math.round(zones.reduce((acc, z) => acc + z.survivalProbability, 0) / zones.length);
  const criticalZones = zones.filter(z => z.riskLevel === 'critical').length;
  const totalPopulation = zones.reduce((acc, z) => acc + z.population, 0);
  const atRiskPopulation = zones
    .filter(z => z.riskLevel === 'critical' || z.riskLevel === 'high')
    .reduce((acc, z) => acc + z.population, 0);

  const getThreatLevel = () => {
    if (criticalZones >= 2) return { level: 'CRITICAL', color: 'text-red-500', bgColor: 'bg-red-500/20' };
    if (criticalZones === 1) return { level: 'HIGH', color: 'text-orange-500', bgColor: 'bg-orange-500/20' };
    if (zones.some(z => z.riskLevel === 'medium')) return { level: 'MEDIUM', color: 'text-yellow-500', bgColor: 'bg-yellow-500/20' };
    return { level: 'LOW', color: 'text-green-500', bgColor: 'bg-green-500/20' };
  };

  const threat = getThreatLevel();

  return (
    <div className="space-y-4">
      {/* Overall Threat Level */}
      <Card className="border-border">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Overall Threat Level</p>
              <p className={`text-2xl font-bold ${threat.color}`}>{threat.level}</p>
            </div>
            <div className={`p-3 rounded-lg ${threat.bgColor}`}>
              <Shield className={`w-6 h-6 ${threat.color}`} />
            </div>
          </div>
          <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
            <span>{criticalZones} Critical Zones</span>
            <span>•</span>
            <span>{atRiskPopulation.toLocaleString()} At Risk</span>
          </div>
        </CardContent>
      </Card>

      {/* Selected Zone or Overall Metrics */}
      {selectedZoneData ? (
        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {selectedZoneData.name}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Damage Severity */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-orange-500" />
                  <span className="text-sm text-foreground">Damage Severity</span>
                </div>
                <span className="text-sm font-bold text-foreground">
                  {selectedZoneData.damageScore}%
                </span>
              </div>
              <Progress 
                value={selectedZoneData.damageScore} 
                className="h-2"
              />
              <div className="flex items-center gap-1 mt-1">
                <TrendingUp className="w-3 h-3 text-red-500" />
                <span className="text-xs text-red-500">Severe structural damage detected</span>
              </div>
            </div>

            {/* Survival Probability */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <HeartPulse className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-foreground">Survival Probability</span>
                </div>
                <span className="text-sm font-bold text-foreground">
                  {selectedZoneData.survivalProbability}%
                </span>
              </div>
              <Progress 
                value={selectedZoneData.survivalProbability} 
                className="h-2"
              />
              <div className="flex items-center gap-1 mt-1">
                {selectedZoneData.survivalProbability < 50 ? (
                  <>
                    <TrendingDown className="w-3 h-3 text-red-500" />
                    <span className="text-xs text-red-500">Critical - Immediate response needed</span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-3 h-3 text-green-500" />
                    <span className="text-xs text-green-500">Stable condition</span>
                  </>
                )}
              </div>
            </div>

            {/* Zone Stats */}
            <div className="pt-2 border-t border-border">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs text-muted-foreground">Population</p>
                  <p className="text-lg font-semibold text-foreground">
                    {selectedZoneData.population.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Risk Level</p>
                  <p className={`text-lg font-semibold capitalize ${
                    selectedZoneData.riskLevel === 'critical' ? 'text-red-500' :
                    selectedZoneData.riskLevel === 'high' ? 'text-orange-500' :
                    selectedZoneData.riskLevel === 'medium' ? 'text-yellow-500' :
                    'text-green-500'
                  }`}>
                    {selectedZoneData.riskLevel}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Overall Metrics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Average Damage */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-orange-500" />
                  <span className="text-sm text-foreground">Avg Damage Severity</span>
                </div>
                <span className="text-sm font-bold text-foreground">{avgDamage}%</span>
              </div>
              <Progress value={avgDamage} className="h-2" />
            </div>

            {/* Average Survival */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <HeartPulse className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-foreground">Avg Survival Probability</span>
                </div>
                <span className="text-sm font-bold text-foreground">{avgSurvival}%</span>
              </div>
              <Progress value={avgSurvival} className="h-2" />
            </div>

            {/* Population Stats */}
            <div className="pt-2 border-t border-border">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs text-muted-foreground">Total Population</p>
                  <p className="text-lg font-semibold text-foreground">
                    {totalPopulation.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">At Risk</p>
                  <p className="text-lg font-semibold text-red-500">
                    {atRiskPopulation.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Zone List */}
      <Card className="border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Zone Overview
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-border">
            {zones.map(zone => (
              <div 
                key={zone.id} 
                className={`px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-muted/50 transition-colors ${
                  selectedZone === zone.id ? 'bg-muted' : ''
                }`}
                onClick={() => {}}
              >
                <div>
                  <p className="text-sm font-medium text-foreground">{zone.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {zone.population.toLocaleString()} people
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <div 
                    className={`w-2 h-2 rounded-full ${
                      zone.riskLevel === 'critical' ? 'bg-red-500 animate-pulse' :
                      zone.riskLevel === 'high' ? 'bg-orange-500' :
                      zone.riskLevel === 'medium' ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                  />
                  <span className={`text-xs font-medium capitalize ${
                    zone.riskLevel === 'critical' ? 'text-red-500' :
                    zone.riskLevel === 'high' ? 'text-orange-500' :
                    zone.riskLevel === 'medium' ? 'text-yellow-500' :
                    'text-green-500'
                  }`}>
                    {zone.riskLevel}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
