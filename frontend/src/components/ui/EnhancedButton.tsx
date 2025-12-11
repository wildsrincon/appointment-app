'use client';

import { cn } from "@/utils/utils";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import * as React from "react";

const enhancedButtonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 active:scale-95 hover:shadow-md",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline:
          "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        success:
          "bg-green-500 text-white shadow hover:bg-green-600",
        warning:
          "bg-yellow-500 text-white shadow hover:bg-yellow-600",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        icon: "h-9 w-9",
        xl: "h-12 rounded-md px-10 text-base",
      },
      state: {
        default: "",
        loading: "opacity-80",
        success: "bg-green-500 hover:bg-green-600 text-white border-green-500",
        error: "bg-red-500 hover:bg-red-600 text-white border-red-500",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      state: "default",
    },
  }
);

export interface EnhancedButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof enhancedButtonVariants> {
  asChild?: boolean;
  loading?: boolean;
  success?: boolean;
  error?: boolean;
  loadingText?: string;
  successText?: string;
  errorText?: string;
  onClick?: () => void | Promise<void>;
}

const EnhancedButton = React.forwardRef<HTMLButtonElement, EnhancedButtonProps>(
  (
    {
      className,
      variant,
      size,
      state,
      asChild = false,
      loading = false,
      success = false,
      error = false,
      loadingText,
      successText,
      errorText,
      children,
      disabled,
      onClick,
      ...props
    },
    ref
  ) => {
    const [internalLoading, setInternalLoading] = React.useState(false);
    const [internalSuccess, setInternalSuccess] = React.useState(false);
    const [internalError, setInternalError] = React.useState(false);

    const isLoading = loading || internalLoading;
    const isSuccess = success || internalSuccess;
    const isError = error || internalError;

    // Auto-reset states
    React.useEffect(() => {
      if (isSuccess) {
        const timer = setTimeout(() => setInternalSuccess(false), 2000);
        return () => clearTimeout(timer);
      }
    }, [isSuccess]);

    React.useEffect(() => {
      if (isError) {
        const timer = setTimeout(() => setInternalError(false), 3000);
        return () => clearTimeout(timer);
      }
    }, [isError]);

    const handleClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
      if (isLoading || disabled) return;

      if (onClick) {
        try {
          setInternalLoading(true);
          await onClick();
          setInternalSuccess(true);
        } catch (err) {
          setInternalError(true);
          console.error('Button action failed:', err);
        } finally {
          setInternalLoading(false);
        }
      }
    };

    // Determine current state
    let currentState = state;
    if (isLoading) currentState = 'loading';
    else if (isSuccess) currentState = 'success';
    else if (isError) currentState = 'error';

    // Determine content to show
    let buttonContent = children;
    if (isLoading && loadingText) {
      buttonContent = (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          {loadingText}
        </>
      );
    } else if (isSuccess && successText) {
      buttonContent = (
        <>
          <CheckCircle className="w-4 h-4" />
          {successText}
        </>
      );
    } else if (isError && errorText) {
      buttonContent = (
        <>
          <AlertCircle className="w-4 h-4" />
          {errorText}
        </>
      );
    } else if (isLoading) {
      buttonContent = (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          {children}
        </>
      );
    } else if (isSuccess) {
      buttonContent = (
        <>
          <CheckCircle className="w-4 h-4" />
          {children}
        </>
      );
    } else if (isError) {
      buttonContent = (
        <>
          <AlertCircle className="w-4 h-4" />
          {children}
        </>
      );
    }

    const Comp = asChild ? Slot : "button";

    return (
      <Comp
        className={cn(enhancedButtonVariants({ variant, size, state: currentState, className }))}
        ref={ref}
        disabled={disabled || isLoading}
        onClick={handleClick}
        aria-disabled={disabled || isLoading}
        aria-busy={isLoading}
        {...props}
      >
        {buttonContent}
      </Comp>
    );
  }
);

EnhancedButton.displayName = "EnhancedButton";

export { EnhancedButton, enhancedButtonVariants };
