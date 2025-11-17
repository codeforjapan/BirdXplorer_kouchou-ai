import type { ReactNode } from "react";
import styles from "./layout.module.css";

export default function ReportLayout({ children }: { children: ReactNode }) {
  return <section className={styles.darkRoot}>{children}</section>;
}

