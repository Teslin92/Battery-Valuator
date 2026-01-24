# Lovable Fix: Chemistry-Specific Metal Inputs

## Problem

When user selects a chemistry type, the UI shows incorrect metals:
- **LCO** shows Manganese and Nickel fields (should only show Li, Co)
- **NCA** shows Manganese field (should only show Ni, Co, Li, Al)

## Solution

Use the `/api/chemistries` endpoint to get the correct primary metals for each chemistry, then dynamically show/hide input fields.

## API Endpoint

```
GET https://battery-valuator-production.up.railway.app/api/chemistries
```

### Response

```json
{
  "success": true,
  "data": {
    "NMC": {
      "name": "Nickel Manganese Cobalt (NMC/NCM)",
      "primary_metals": ["Nickel", "Cobalt", "Lithium", "Manganese"],
      "typical_grades": {
        "Nickel": [0.10, 0.50],
        "Cobalt": [0.03, 0.20],
        "Lithium": [0.03, 0.07],
        "Manganese": [0.02, 0.15]
      }
    },
    "LFP": {
      "name": "Lithium Iron Phosphate (LFP)",
      "primary_metals": ["Lithium", "Iron", "Phosphorus"],
      "typical_grades": {
        "Lithium": [0.04, 0.07],
        "Iron": [0.30, 0.35],
        "Phosphorus": [0.15, 0.20]
      }
    },
    "LCO": {
      "name": "Lithium Cobalt Oxide (LCO)",
      "primary_metals": ["Lithium", "Cobalt"],
      "typical_grades": {
        "Lithium": [0.05, 0.08],
        "Cobalt": [0.40, 0.60]
      }
    },
    "NCA": {
      "name": "Nickel Cobalt Aluminum (NCA)",
      "primary_metals": ["Nickel", "Cobalt", "Lithium", "Aluminum"],
      "typical_grades": {
        "Nickel": [0.45, 0.55],
        "Cobalt": [0.08, 0.12],
        "Lithium": [0.05, 0.08],
        "Aluminum": [0.01, 0.03]
      }
    }
  }
}
```

## Correct Metal Fields Per Chemistry

| Chemistry | Show These Metals | Hide These Metals |
|-----------|-------------------|-------------------|
| **NMC** | Ni, Co, Li, Mn, Cu, Al | Fe, P |
| **LFP** | Li, Fe, P | Ni, Co, Mn |
| **LCO** | Li, Co | Ni, Mn, Fe, P |
| **NCA** | Ni, Co, Li, Al, Cu | Mn, Fe, P |

**Note:** Cu (Copper) is always optional as it can be a trace contaminant in any chemistry.

## Implementation

### 1. Fetch Chemistries on Load

```typescript
const [chemistries, setChemistries] = useState({});

useEffect(() => {
  fetch('https://battery-valuator-production.up.railway.app/api/chemistries')
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        setChemistries(data.data);
      }
    });
}, []);
```

### 2. Get Primary Metals for Selected Chemistry

```typescript
const getPrimaryMetals = (chemistryCode: string) => {
  const chemistry = chemistries[chemistryCode];
  if (!chemistry) return ['Nickel', 'Cobalt', 'Lithium', 'Copper', 'Aluminum', 'Manganese'];

  // Always include Copper as optional trace metal
  const metals = [...chemistry.primary_metals];
  if (!metals.includes('Copper')) {
    metals.push('Copper');
  }
  return metals;
};
```

### 3. Conditionally Render Metal Inputs

```tsx
// All possible metals
const ALL_METALS = [
  { key: 'Nickel', label: 'Ni', symbol: 'Ni' },
  { key: 'Cobalt', label: 'Co', symbol: 'Co' },
  { key: 'Lithium', label: 'Li', symbol: 'Li' },
  { key: 'Manganese', label: 'Mn', symbol: 'Mn' },
  { key: 'Copper', label: 'Cu', symbol: 'Cu' },
  { key: 'Aluminum', label: 'Al', symbol: 'Al' },
  { key: 'Iron', label: 'Fe', symbol: 'Fe' },
  { key: 'Phosphorus', label: 'P', symbol: 'P' },
];

// In your component
const primaryMetals = getPrimaryMetals(selectedChemistry);

return (
  <div className="grid grid-cols-3 gap-4">
    {ALL_METALS.map(metal => {
      // Only show if this metal is primary for the selected chemistry
      const isVisible = primaryMetals.includes(metal.key);

      if (!isVisible) return null;

      return (
        <div key={metal.key}>
          <Label>{metal.label} (%)</Label>
          <Input
            type="number"
            step="0.1"
            min="0"
            max="100"
            value={assays[metal.key] || ''}
            onChange={(e) => handleAssayChange(metal.key, e.target.value)}
            placeholder={getPlaceholder(metal.key, selectedChemistry)}
          />
        </div>
      );
    })}
  </div>
);
```

### 4. Show Typical Range Placeholders

```typescript
const getPlaceholder = (metalKey: string, chemistryCode: string) => {
  const chemistry = chemistries[chemistryCode];
  if (!chemistry?.typical_grades?.[metalKey]) return '0.0';

  const [min, max] = chemistry.typical_grades[metalKey];
  return `${(min * 100).toFixed(0)}-${(max * 100).toFixed(0)}%`;
};
```

### 5. Reset Non-Primary Metals on Chemistry Change

```typescript
const handleChemistryChange = (newChemistry: string) => {
  setSelectedChemistry(newChemistry);

  // Reset assays for metals not in the new chemistry
  const primaryMetals = getPrimaryMetals(newChemistry);
  const newAssays = { ...assays };

  ALL_METALS.forEach(metal => {
    if (!primaryMetals.includes(metal.key)) {
      newAssays[metal.key] = 0;  // Reset to 0
    }
  });

  setAssays(newAssays);
};
```

## Example: What User Should See

### When "LCO" is Selected

```
Chemistry: [LCO - Lithium Cobalt Oxide ▼]

Metal Composition:
┌─────────────┬─────────────┐
│ Li (%)      │ Co (%)      │
│ [5.0-8.0%]  │ [40-60%]    │
└─────────────┴─────────────┘

Optional:
┌─────────────┐
│ Cu (%)      │
│ [0.0]       │
└─────────────┘
```

### When "NCA" is Selected

```
Chemistry: [NCA - Nickel Cobalt Aluminum ▼]

Metal Composition:
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Ni (%)      │ Co (%)      │ Li (%)      │ Al (%)      │
│ [45-55%]    │ [8-12%]     │ [5-8%]      │ [1-3%]      │
└─────────────┴─────────────┴─────────────┴─────────────┘

Optional:
┌─────────────┐
│ Cu (%)      │
│ [0.0]       │
└─────────────┘
```

### When "LFP" is Selected

```
Chemistry: [LFP - Lithium Iron Phosphate ▼]

Metal Composition:
┌─────────────┬─────────────┬─────────────┐
│ Li (%)      │ Fe (%)      │ P (%)       │
│ [4-7%]      │ [30-35%]    │ [15-20%]    │
└─────────────┴─────────────┴─────────────┘
```

## Testing Checklist

After implementing, verify:

- [ ] Selecting **LCO** shows ONLY: Li, Co (+ optional Cu)
- [ ] Selecting **NCA** shows ONLY: Ni, Co, Li, Al (+ optional Cu)
- [ ] Selecting **LFP** shows ONLY: Li, Fe, P
- [ ] Selecting **NMC** shows: Ni, Co, Li, Mn, Cu, Al
- [ ] Changing chemistry resets hidden metal values to 0
- [ ] Placeholder text shows typical ranges for each chemistry
- [ ] Calculations still work correctly with reduced metal inputs
