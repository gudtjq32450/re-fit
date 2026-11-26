import { defineStore } from "pinia";
import apiClient from "../api/client";

export const useStudioStore = defineStore("studio", {
  state: () => ({
    prompt: "",
    garmentType: "HOODIE",
    color: "#1f2937",
    gsmWeight: 480,
    roughness: 0.78,
    doubleLayered: true,
    oversizedHood: true,
    size: "L",
    printingText: "RE:FIT",
    estimatedCost: 70000,
    recommendedDeposit: 85000,
    costBreakdown: null,
    styleAnalysis: null,
  }),
  actions: {
    async analyzeStyle() {
      const { data } = await apiClient.post("/ai/style-analyze/", {
        prompt: this.prompt,
      });
      this.styleAnalysis = data;
      return data;
    },
    async estimateCost() {
      const { data } = await apiClient.post("/ai/estimate-cost/", {
        garment_type: this.garmentType,
        gsm_weight: this.gsmWeight,
        double_layered: this.doubleLayered,
        oversized_hood: this.oversizedHood,
        printing_text: this.printingText,
        target_quantity: 100,
      });
      this.estimatedCost = data.estimated_unit_cost;
      this.recommendedDeposit = data.recommended_deposit;
      this.costBreakdown = data.breakdown;
      return data;
    },
  },
});
