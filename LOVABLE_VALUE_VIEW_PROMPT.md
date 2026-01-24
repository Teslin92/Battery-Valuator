# Lovable Update: Value View & Bid Report Features

## Overview

Two new API endpoints are available to support OEM and Trader user personas:

1. **Value View** (`/api/value-view`) - Simple valuation for OEMs
2. **Bid Report** (`/api/bid-report`) - Exportable quotes for Traders

---

## 1. Value View - Simple Mode for OEMs

**Purpose:** OEMs just want to know "what's my scrap worth?" without seeing processing costs or margins.

### API Endpoint

```
POST https://battery-valuator-production.up.railway.app/api/value-view
```

### Request

```json
{
  "currency": "USD",
  "weight_kg": 1000,
  "assays": {
    "Nickel": 0.205,
    "Cobalt": 0.062,
    "Lithium": 0.025,
    "Copper": 0.015,
    "Aluminum": 0.008,
    "Manganese": 0.045
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "summary": {
      "weight_kg": 1000,
      "currency": "USD",
      "chemistry": "NMC",
      "chemistry_name": "Nickel Manganese Cobalt (NMC/NCM)",
      "total_estimated_value": 4125.50,
      "value_per_tonne": 4125.50,
      "price_date": "2025-01-24 10:30:00"
    },
    "metal_breakdown": [
      {
        "metal": "Nickel",
        "grade_pct": 20.5,
        "contained_kg": 205.0,
        "recoverable_kg": 194.75,
        "recovery_rate_pct": 95,
        "estimated_value": 2570.50
      },
      {
        "metal": "Cobalt",
        "grade_pct": 6.2,
        "contained_kg": 62.0,
        "recoverable_kg": 58.90,
        "recovery_rate_pct": 95,
        "estimated_value": 1458.20
      }
      // ... more metals
    ],
    "notes": [
      "Values based on current market prices and typical industry recovery rates",
      "Actual offers may vary based on material condition, volume, and processor terms",
      "Chemistry auto-detected as Nickel Manganese Cobalt (NMC/NCM)"
    ]
  }
}
```

### UI Implementation

Create a simplified view/tab called "Quick Valuation" or "OEM View":

```tsx
// Minimal inputs needed
<Card>
  <CardHeader>
    <CardTitle>Quick Valuation</CardTitle>
    <CardDescription>Get a simple estimate of your battery scrap value</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="space-y-4">
      {/* Weight input */}
      <Input
        label="Material Weight (kg)"
        type="number"
        value={weight}
        onChange={(e) => setWeight(e.target.value)}
      />

      {/* Currency selector */}
      <Select value={currency} onValueChange={setCurrency}>
        <SelectItem value="USD">USD</SelectItem>
        <SelectItem value="CAD">CAD</SelectItem>
        <SelectItem value="EUR">EUR</SelectItem>
      </Select>

      {/* Assay inputs - simplified grid */}
      <div className="grid grid-cols-3 gap-4">
        <Input label="Ni %" type="number" step="0.1" />
        <Input label="Co %" type="number" step="0.1" />
        <Input label="Li %" type="number" step="0.1" />
        <Input label="Cu %" type="number" step="0.1" />
        <Input label="Mn %" type="number" step="0.1" />
        <Input label="Fe %" type="number" step="0.1" />
      </div>

      <Button onClick={calculateValue}>Get Estimate</Button>
    </div>
  </CardContent>
</Card>

{/* Results display */}
{result && (
  <Card className="mt-4">
    <CardHeader>
      <CardTitle>Estimated Value</CardTitle>
      <Badge>{result.summary.chemistry_name}</Badge>
    </CardHeader>
    <CardContent>
      <div className="text-4xl font-bold text-green-600">
        {currency} {result.summary.total_estimated_value.toLocaleString()}
      </div>
      <div className="text-muted-foreground">
        ({currency} {result.summary.value_per_tonne.toLocaleString()} per tonne)
      </div>

      {/* Metal breakdown table */}
      <Table className="mt-4">
        <TableHeader>
          <TableRow>
            <TableHead>Metal</TableHead>
            <TableHead>Grade</TableHead>
            <TableHead>Recoverable</TableHead>
            <TableHead>Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {result.metal_breakdown.map((metal) => (
            <TableRow key={metal.metal}>
              <TableCell>{metal.metal}</TableCell>
              <TableCell>{metal.grade_pct}%</TableCell>
              <TableCell>{metal.recoverable_kg.toFixed(1)} kg</TableCell>
              <TableCell>{currency} {metal.estimated_value.toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
)}
```

---

## 2. Bid Report - For Traders

**Purpose:** Generate shareable quotes that hide internal costs and margins.

### API Endpoint

```
POST https://battery-valuator-production.up.railway.app/api/bid-report
```

### Request

```json
{
  "currency": "USD",
  "weight_kg": 10000,
  "assays": {
    "Nickel": 0.205,
    "Cobalt": 0.062,
    "Lithium": 0.025,
    "Copper": 0.015,
    "Aluminum": 0.008,
    "Manganese": 0.045
  },
  "offered_price_per_kg": 2.50,
  "validity_days": 7,
  "transport_origin": "CA",
  "transport_destination": "US",
  "include_transport_advisory": true,
  "include_market_prices": true,
  "company_name": "ABC Recycling Inc.",
  "reference_number": "Q-2025-0042"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "report_info": {
      "type": "Battery Material Purchase Quote",
      "date": "2025-01-24",
      "valid_until": "2025-01-31",
      "reference": "Q-2025-0042",
      "company": "ABC Recycling Inc."
    },
    "material": {
      "weight_kg": 10000,
      "weight_tonnes": 10.0,
      "chemistry": "NMC",
      "chemistry_name": "Nickel Manganese Cobalt (NMC/NCM)",
      "composition": [
        {"metal": "Nickel", "grade_pct": 20.5, "contained_kg": 2050.0, "market_price_per_kg": 16.50},
        {"metal": "Cobalt", "grade_pct": 6.2, "contained_kg": 620.0, "market_price_per_kg": 33.00}
        // ... more metals
      ]
    },
    "pricing": {
      "currency": "USD",
      "market_price_date": "2025-01-24 10:30:00",
      "offered_price_per_kg": 2.50,
      "total_offered_value": 25000.00
    },
    "transport": {
      "route": "Canada → United States",
      "status": "Regulated",
      "key_requirements": ["EPA Notification", "RCRA Manifest", "Canadian Export Permit"],
      "estimated_cost": "$150-400 per tonne",
      "transit_time": "3-7 business days"
    },
    "disclaimer": "This quote is subject to material inspection..."
  }
}
```

### UI Implementation

Create a "Generate Quote" section in the trader/advanced view:

```tsx
// Quote generation form
<Card>
  <CardHeader>
    <CardTitle>Generate Quote</CardTitle>
    <CardDescription>Create a shareable bid document</CardDescription>
  </CardHeader>
  <CardContent>
    <div className="grid grid-cols-2 gap-4">
      {/* Company branding */}
      <Input
        label="Your Company Name"
        value={companyName}
        onChange={(e) => setCompanyName(e.target.value)}
      />
      <Input
        label="Reference Number"
        value={reference}
        onChange={(e) => setReference(e.target.value)}
      />

      {/* Offer details */}
      <Input
        label={`Offered Price (${currency}/kg)`}
        type="number"
        step="0.01"
        value={offeredPrice}
        onChange={(e) => setOfferedPrice(e.target.value)}
      />
      <Input
        label="Validity (days)"
        type="number"
        value={validityDays}
        onChange={(e) => setValidityDays(e.target.value)}
      />

      {/* Transport (optional) */}
      <Select label="Origin Country">
        <SelectItem value="CA">Canada</SelectItem>
        <SelectItem value="US">United States</SelectItem>
        <SelectItem value="DE">Germany</SelectItem>
        {/* ... more countries */}
      </Select>
      <Select label="Destination Country">
        {/* ... same options */}
      </Select>

      {/* Options */}
      <div className="col-span-2 space-y-2">
        <Checkbox
          label="Include market prices"
          checked={includeMarketPrices}
          onCheckedChange={setIncludeMarketPrices}
        />
        <Checkbox
          label="Include transport advisory"
          checked={includeTransport}
          onCheckedChange={setIncludeTransport}
        />
      </div>
    </div>

    <Button onClick={generateReport} className="mt-4">
      Generate Quote
    </Button>
  </CardContent>
</Card>

{/* Quote preview - formatted for printing/export */}
{report && (
  <Card className="mt-4 print:shadow-none">
    <CardHeader className="border-b">
      <div className="flex justify-between items-start">
        <div>
          <CardTitle>{report.report_info.company || "Battery Material Quote"}</CardTitle>
          <CardDescription>Reference: {report.report_info.reference}</CardDescription>
        </div>
        <div className="text-right text-sm text-muted-foreground">
          <div>Date: {report.report_info.date}</div>
          <div>Valid Until: {report.report_info.valid_until}</div>
        </div>
      </div>
    </CardHeader>
    <CardContent className="space-y-6 pt-4">
      {/* Material details */}
      <div>
        <h3 className="font-semibold mb-2">Material Specification</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>Weight: {report.material.weight_tonnes} tonnes</div>
          <div>Chemistry: {report.material.chemistry_name}</div>
        </div>
        <Table className="mt-2">
          {/* Composition table */}
        </Table>
      </div>

      {/* Pricing */}
      <div>
        <h3 className="font-semibold mb-2">Pricing</h3>
        <div className="text-2xl font-bold">
          {report.pricing.currency} {report.pricing.total_offered_value.toLocaleString()}
        </div>
        <div className="text-muted-foreground">
          @ {report.pricing.currency} {report.pricing.offered_price_per_kg}/kg
        </div>
      </div>

      {/* Transport (if included) */}
      {report.transport && (
        <div>
          <h3 className="font-semibold mb-2">Transport Notes</h3>
          <div className="text-sm space-y-1">
            <div>Route: {report.transport.route}</div>
            <div>Status: <Badge>{report.transport.status}</Badge></div>
            <div>Est. Cost: {report.transport.estimated_cost}</div>
            <div>Transit: {report.transport.transit_time}</div>
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="text-xs text-muted-foreground border-t pt-4">
        {report.disclaimer}
      </div>
    </CardContent>

    <CardFooter className="print:hidden">
      <Button onClick={() => window.print()}>Print Quote</Button>
      <Button variant="outline" onClick={exportToPDF}>Export PDF</Button>
    </CardFooter>
  </Card>
)}
```

---

## 3. Navigation Structure

Suggest adding tabs or a mode selector:

```tsx
<Tabs defaultValue="advanced">
  <TabsList>
    <TabsTrigger value="quick">Quick Valuation</TabsTrigger>
    <TabsTrigger value="advanced">Full Analysis</TabsTrigger>
    <TabsTrigger value="quote">Generate Quote</TabsTrigger>
  </TabsList>

  <TabsContent value="quick">
    {/* Value View UI */}
  </TabsContent>

  <TabsContent value="advanced">
    {/* Existing full calculator */}
  </TabsContent>

  <TabsContent value="quote">
    {/* Bid Report UI */}
  </TabsContent>
</Tabs>
```

---

## 4. Key Points

**Value View:**
- No processing costs shown
- No margins shown
- Uses typical industry recovery rates
- Perfect for OEMs who just want to know their scrap value

**Bid Report:**
- Intentionally hides internal costs
- Intentionally hides trader margins
- Shareable with suppliers
- Includes optional transport advisory
- Professional formatting for export

**What's Hidden (by design):**
- Processing/shredding costs
- Refining OPEX
- Trader's margin calculation
- Sensitivity analysis
- Internal payable rates (uses standard rates)

This ensures traders can share quotes without revealing their competitive advantage.
