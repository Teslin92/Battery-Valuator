import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { ProductionItem } from '@/types/battery';

interface ProductTableProps {
  products: ProductionItem[];
  currency: string;
}

export function ProductTable({ products, currency }: ProductTableProps) {
  const formatCurrency = (value: number) => {
    const symbol = currency === 'EUR' ? '€' : currency === 'CNY' ? '¥' : '$';
    return `${symbol}${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const totalMass = products.reduce((sum, p) => sum + p['Mass (kg)'], 0);
  const totalRevenue = products.reduce((sum, p) => sum + p.Revenue, 0);

  return (
    <div className="bg-card rounded-xl border border-border p-6 card-shadow">
      <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-4">
        Product Schedule
      </h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="font-semibold">Product</TableHead>
            <TableHead className="text-right font-semibold">Mass (kg)</TableHead>
            <TableHead className="text-right font-semibold">Revenue</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {products.map((product, idx) => (
            <TableRow key={idx}>
              <TableCell className="font-medium">{product.Product}</TableCell>
              <TableCell className="text-right font-mono">
                {product['Mass (kg)'].toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </TableCell>
              <TableCell className="text-right font-mono text-profit">
                {formatCurrency(product.Revenue)}
              </TableCell>
            </TableRow>
          ))}
          <TableRow className="bg-secondary/50 font-semibold">
            <TableCell>Total</TableCell>
            <TableCell className="text-right font-mono">
              {totalMass.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </TableCell>
            <TableCell className="text-right font-mono text-profit">
              {formatCurrency(totalRevenue)}
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
