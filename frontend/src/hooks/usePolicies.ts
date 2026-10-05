import { useQuery } from "@tanstack/react-query";
import { fetchPolicies } from "@/lib/api";

export function usePolicies() {
  return useQuery({
    queryKey: ["policies"],
    queryFn: fetchPolicies,
  });
}
