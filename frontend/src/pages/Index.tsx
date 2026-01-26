import { useRef } from 'react';
import { Play, Battery, TrendingUp, Download, Coffee } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { GlobalSettings } from '@/components/valuator/GlobalSettings';
import { FeedstockSection } from '@/components/valuator/FeedstockSection';
import { PricingSection } from '@/components/valuator/PricingSection';
import { RefiningSection } from '@/components/valuator/RefiningSection';
import { AssaySection } from '@/components/valuator/AssaySection';
import { ResultsPanel } from '@/components/valuator/ResultsPanel';
import { useBatteryValuator } from '@/hooks/useBatteryValuator';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const Index = () => {
  const resultsRef = useRef<HTMLDivElement>(null);
  
  const {
    formData,
    updateFormData,
    updateFeedType,
    updateFxRate,
    resetFxRate,
    result,
    marketData,
    isLoadingMarket,
    marketError,
    refetchMarket,
    handleParseCOA,
    isParsingCOA,
    handleCalculate,
    isCalculating,
    recoverableBlackMass,
  } = useBatteryValuator();

  const handleExportPDF = async () => {
    if (!resultsRef.current || !result) return;
    
    // Wait for any pending renders
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const canvas = await html2canvas(resultsRef.current, {
      scale: 2,
      backgroundColor: '#FAFAFA',
      logging: false,
      useCORS: true,
      allowTaint: true,
      windowWidth: 1200, // Force consistent width for better alignment
    });
    
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });
    
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const imgWidth = pdfWidth - 20; // 10mm margins on each side
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    
    // Add header
    pdf.setFontSize(18);
    pdf.setTextColor(27, 94, 32);
    pdf.text('Battery Valuator Report', 10, 15);
    
    pdf.setFontSize(9);
    pdf.setTextColor(100, 100, 100);
    pdf.text(`Generated: ${new Date().toLocaleString()}`, 10, 22);
    pdf.text(`Material: ${formData.feedType} | Gross Weight: ${formData.grossWeight.toLocaleString()} kg | Net BM: ${result.net_bm_weight.toLocaleString(undefined, { maximumFractionDigits: 1 })} kg`, 10, 27);
    
    // Add results image - properly centered
    const yOffset = 32;
    
    // Check if image fits on page, otherwise scale down
    const maxImgHeight = pdfHeight - yOffset - 10;
    const finalImgHeight = Math.min(imgHeight, maxImgHeight);
    const finalImgWidth = (finalImgHeight / imgHeight) * imgWidth;
    const xOffset = (pdfWidth - finalImgWidth) / 2;
    
    pdf.addImage(imgData, 'PNG', xOffset, yOffset, finalImgWidth, finalImgHeight);
    
    pdf.save(`battery-valuation-${Date.now()}.pdf`);
  };

  return (
    <div className="min-h-screen w-full bg-background">
      <ScrollArea className="h-screen">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Support Banner */}
          <div className="flex justify-center mb-4">
            <a
              href="https://buymeacoffee.com/zmeseldzijv"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
            >
              <Coffee className="h-4 w-4" />
              Support this project
            </a>
          </div>

          {/* Header */}
          <header className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl profit-gradient flex items-center justify-center">
                <Battery className="h-6 w-6 text-profit-foreground" />
              </div>
              <div>
                <h1 className="font-bold text-2xl text-foreground">Battery Valuator</h1>
                <p className="text-sm text-muted-foreground">Material Valuation Tool</p>
              </div>
            </div>
            {result && (
              <Button
                onClick={handleExportPDF}
                variant="outline"
                className="gap-2"
              >
                <Download className="h-4 w-4" />
                Export PDF
              </Button>
            )}
          </header>

          {/* Input Sections */}
          <div className="space-y-6 mb-8">
            {/* Global Settings Card */}
            <section className="bg-card rounded-xl border border-border p-6 card-shadow">
              <GlobalSettings
                currency={formData.currency}
                onCurrencyChange={(currency) => updateFormData({ currency, fxRateOverridden: false })}
                fxRate={formData.fxRate}
                fxRateOverridden={formData.fxRateOverridden}
                onFxRateChange={updateFxRate}
                onResetFxRate={resetFxRate}
                marketData={marketData}
                isLoading={isLoadingMarket}
                onRefresh={() => refetchMarket()}
                error={marketError ?? undefined}
              />
            </section>

            {/* Feedstock & Pre-treatment Card */}
            <section className="bg-card rounded-xl border border-border p-6 card-shadow">
              <FeedstockSection
                formData={formData}
                onUpdate={updateFormData}
                onFeedTypeChange={updateFeedType}
                recoverableBlackMass={recoverableBlackMass}
              />
            </section>

            {/* Lab Assay Card - Moved after Feedstock */}
            <section className="bg-card rounded-xl border border-border p-6 card-shadow">
              <AssaySection
                formData={formData}
                onUpdate={updateFormData}
                onParseCOA={handleParseCOA}
                isParsing={isParsingCOA}
              />
            </section>

            {/* Two-column grid for Pricing and Refining */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <section className="bg-card rounded-xl border border-border p-6 card-shadow">
                <PricingSection
                  formData={formData}
                  onUpdate={updateFormData}
                  marketData={marketData}
                />
              </section>

              <section className="bg-card rounded-xl border border-border p-6 card-shadow">
                <RefiningSection formData={formData} onUpdate={updateFormData} />
              </section>
            </div>
          </div>

          {/* Calculate Button */}
          <div className="mb-10">
            <Button
              onClick={handleCalculate}
              disabled={isCalculating}
              size="lg"
              className="w-full profit-gradient hover:opacity-90 transition-opacity gap-3 text-base font-semibold h-14"
            >
              <Play className={`h-5 w-5 ${isCalculating ? 'animate-pulse' : ''}`} />
              {isCalculating ? 'Calculating...' : 'Run Valuation'}
            </Button>
          </div>

          <Separator className="mb-10" />

          {/* Results Section */}
          <section ref={resultsRef}>
            {!result ? (
              <div className="flex flex-col items-center justify-center py-16 text-center px-8">
                <div className="w-20 h-20 rounded-full bg-secondary flex items-center justify-center mb-6">
                  <TrendingUp className="h-10 w-10 text-muted-foreground" />
                </div>
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Ready to Calculate
                </h2>
                <p className="text-muted-foreground max-w-md">
                  Configure your inputs above and click "Run Valuation" to see your battery material valuation results.
                </p>
              </div>
            ) : (
              <ResultsPanel
                result={result}
                formData={formData}
                recoverableBlackMass={recoverableBlackMass}
                isCalculating={isCalculating}
              />
            )}
          </section>

          {/* Footer with Support Link */}
          <div className="flex justify-center py-8">
            <a
              href="https://buymeacoffee.com/zmeseldzijv"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
            >
              <Coffee className="h-4 w-4" />
              Buy me a coffee
            </a>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
};

export default Index;
