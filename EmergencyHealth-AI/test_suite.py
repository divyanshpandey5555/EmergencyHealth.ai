"""
AI EMERGENCY HEALTH ASSISTANT - COMPREHENSIVE TEST SUITE
Matches validation test cases from ITM University Gwalior presentation.
Includes verification of proper generic and brand medication names.
"""

import unittest
from triage_engine import evaluate_clinical_rules

class TestEmergencyHealthAssistant(unittest.TestCase):

    def test_case_1_general_mild_headache(self):
        """Test Case 1 (General): 'I have a mild headache'"""
        result = evaluate_clinical_rules("I have a mild headache")
        self.assertEqual(result["level"], "GENERAL")
        self.assertIn("rest", result["immediate_action"].lower())
        self.assertTrue(len(result["precautions"]) > 0)
        self.assertTrue(len(result["next_steps"]) > 0)
        self.assertIn("doctor", result["professional_help"].lower())
        self.assertIn("disclaimer", result)
        
        # Medication verification: Paracetamol or Ibuprofen
        med_names = " ".join([m["name"] for m in result.get("medications", [])]).lower()
        self.assertTrue("paracetamol" in med_names or "ibuprofen" in med_names or "crocin" in med_names)

    def test_case_2_caution_fever_vomiting(self):
        """Test Case 2 (Caution): 'Fever for 3 days with vomiting'"""
        result = evaluate_clinical_rules("Fever for 3 days with vomiting")
        self.assertEqual(result["level"], "CAUTION")
        self.assertTrue(
            "hydration" in result["immediate_action"].lower() or 
            "rehydration" in result["immediate_action"].lower() or
            "ors" in result["immediate_action"].lower() or
            "doctor" in result["immediate_action"].lower()
        )
        self.assertTrue(len(result["precautions"]) > 0)
        self.assertTrue(len(result["next_steps"]) > 0)
        self.assertIn("doctor", result["professional_help"].lower())

        # Medication verification: ORS and Paracetamol
        med_names = " ".join([m["name"] for m in result.get("medications", [])]).lower()
        self.assertTrue("ors" in med_names or "rehydration" in med_names or "electral" in med_names)
        self.assertTrue("paracetamol" in med_names or "crocin" in med_names or "dolo" in med_names)

    def test_case_3_emergency_uncontrolled_bleeding(self):
        """Test Case 3 (Emergency): 'Bleeding that will not stop'"""
        result = evaluate_clinical_rules("Bleeding that will not stop")
        self.assertEqual(result["level"], "EMERGENCY")
        self.assertTrue(
            "112" in result["immediate_action"] or 
            "ambulance" in result["immediate_action"].lower()
        )
        self.assertIn("pressure", result["immediate_action"].lower())
        self.assertTrue(len(result["precautions"]) > 0)

        # Medication / First-Aid supplies verification: Betadine / Gauze / avoid aspirin
        med_names = " ".join([m["name"] for m in result.get("medications", [])]).lower()
        self.assertTrue("betadine" in med_names or "povidone" in med_names or "gauze" in med_names)

    def test_case_4_emergency_sample_interaction(self):
        """Test Case 4 (Sample Interaction): 'My father has chest pain and is sweating a lot. What should I do?'"""
        result = evaluate_clinical_rules("My father has chest pain and is sweating a lot. What should I do?")
        self.assertEqual(result["level"], "EMERGENCY")
        self.assertTrue(
            "112" in result["immediate_action"] or 
            "ambulance" in result["immediate_action"].lower()
        )
        self.assertTrue(
            "sit" in result["immediate_action"].lower() or 
            "rest" in result["immediate_action"].lower() or
            "loosen" in result["immediate_action"].lower()
        )
        self.assertIn("not let him walk", " ".join(result["precautions"]).lower())

        # Medication verification: Chewable Aspirin / Nitroglycerin
        med_names = " ".join([m["name"] for m in result.get("medications", [])]).lower()
        self.assertTrue("aspirin" in med_names or "dispirin" in med_names or "sorbitrate" in med_names)

    def test_case_5_vague_input(self):
        """Test Case 5 (Vague input): 'I don't feel good'"""
        result = evaluate_clinical_rules("I don't feel good")
        self.assertEqual(result["level"], "CLARIFICATION")
        self.assertTrue(len(result["next_steps"]) > 0)

    def test_case_6_non_health(self):
        """Test Case 6 (Non-health): 'Write me a poem'"""
        result = evaluate_clinical_rules("Write me a poem")
        self.assertEqual(result["level"], "REDIRECT")
        self.assertTrue(
            "health" in result["immediate_action"].lower() or 
            "medical" in result["immediate_action"].lower()
        )

    def test_structure_conformance(self):
        """Verify all response dictionaries follow the mandatory JSON contract including 'medications'."""
        test_inputs = [
            "mild cough",
            "sprained my wrist yesterday",
            "severe shortness of breath",
            "help",
            "who are you"
        ]
        required_keys = ["level", "immediate_action", "information", "precautions", "medications", "next_steps", "professional_help", "disclaimer"]
        for inp in test_inputs:
            res = evaluate_clinical_rules(inp)
            for k in required_keys:
                self.assertIn(k, res, f"Missing key '{k}' for input '{inp}'")

if __name__ == "__main__":
    unittest.main()
