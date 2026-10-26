import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ShadowByte | Cyber Operations",
  description: "Security operations and authorized assessment workspace."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
