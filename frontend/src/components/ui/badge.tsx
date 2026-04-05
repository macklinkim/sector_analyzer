import { type VariantProps, cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-slate-700 text-slate-100",
        bullish: "border-transparent bg-bullish/20 text-bullish",
        bearish: "border-transparent bg-bearish/20 text-bearish",
        goldilocks: "border-transparent bg-goldilocks/20 text-goldilocks",
        reflation: "border-transparent bg-reflation/20 text-reflation",
        stagflation: "border-transparent bg-stagflation/20 text-stagflation",
        deflation: "border-transparent bg-deflation/20 text-deflation",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
