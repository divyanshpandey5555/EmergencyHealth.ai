"""
AI EMERGENCY HEALTH ASSISTANT - CLINICAL TRIAGE ENGINE
Department of CSA, SOET, ITM University Gwalior
Authors: Nitin Kushwah, Divyansh Pandey, Vinayak Dangi, Aditya Kumar Yadav
Supervisor: Dr. Aravendra Sharma
"""

import re
import json

def evaluate_clinical_rules(query: str) -> dict:
    """
    Evaluates raw health query and classifies into 3-tier safety flow:
    - GENERAL: Minor, non-urgent concerns
    - CAUTION: Symptoms that may get worse
    - EMERGENCY: Possible life-threatening signs
    Also handles CLARIFICATION (vague input) and REDIRECT (non-health).
    Includes proper generic and brand-name medications, dosages, and safety contraindications.
    """
    q = (query or "").lower().strip()

    # 1. Non-Health Queries (PPT Test Case: "Write me a poem")
    non_health_patterns = [
        r"write (me )?(a )?(poem|story|code|essay|song)",
        r"who (is|are) you",
        r"what is (the )?(capital|weather|meaning of life)",
        r"tell me a joke",
        r"sing a song",
        r"who won the match",
        r"python code",
        r"hello world"
    ]
    if any(re.search(pat, q) for pat in non_health_patterns):
        return {
            "level": "REDIRECT",
            "summary": "Non-health query detected.",
            "immediate_action": "Please ask a question related to health, medical symptoms, or emergency first-aid.",
            "information": "I am a dedicated AI Emergency Health Assistant designed specifically to provide triage guidance, basic precautions, first-aid medicines, and instructions for medical concerns.",
            "precautions": [
                "This system is specialized strictly for health and medical emergency triage.",
                "General inquiries, creative writing, or non-medical topics are out of scope."
            ],
            "medications": [],
            "next_steps": [
                "Describe any physical symptoms you or someone nearby is experiencing.",
                "Mention specific details such as duration, severity, and pain location."
            ],
            "professional_help": "For medical concerns, I am here to assist. For non-medical tasks, please use a general-purpose assistant.",
            "disclaimer": "General guidance prototype developed at ITM University Gwalior."
        }

    # 2. Vague Inputs (PPT Test Case: "I don't feel good")
    vague_patterns = [
        r"^(i )?(don't|do not) feel (good|well|right|fine)$",
        r"^(i )?feel sick$",
        r"^help( me)?$",
        r"^i am unwell$",
        r"^not feeling well$",
        r"^something is wrong$"
    ]
    if any(re.search(pat, q) for pat in vague_patterns) or len(q) < 5:
        return {
            "level": "CLARIFICATION",
            "summary": "Your description is general. Additional symptom details are required for accurate triage.",
            "immediate_action": "Sit down comfortably, take deep breaths, and let us know what specific symptoms you have.",
            "information": "To provide the safest and most helpful guidance, we need to know what you are physically experiencing.",
            "precautions": [
                "Do not take random medications before identifying where the pain or symptoms are originating.",
                "If you feel severe pain, dizziness, or difficulty breathing, call 112 immediately."
            ],
            "medications": [
                {
                    "name": "Oral Rehydration / Water",
                    "type": "OTC Support",
                    "dose": "1-2 glasses of water or electrolyte drink",
                    "purpose": "General hydration while evaluating symptoms",
                    "instructions": "Sip slowly while resting comfortably",
                    "warning": "Do not self-prescribe antibiotics or strong painkillers until specific symptoms are verified."
                }
            ],
            "next_steps": [
                "Where do you feel discomfort (e.g. head, chest, abdomen, throat)?",
                "How long have you felt this way (hours, days)?",
                "Do you have accompanying symptoms like fever, nausea, or sweating?"
            ],
            "professional_help": "If your condition suddenly deteriorates, seek prompt medical care at a nearby clinic or call 112.",
            "disclaimer": "General guidance only. Does not replace professional clinical evaluation."
        }

    # 3. EMERGENCY Conditions (PPT: "Bleeding that will not stop", "chest pain & sweating")
    emergency_patterns = [
        r"(chest pain|tightness in chest|chest pressure|crushing chest)",
        r"(chest.*sweat|sweat.*chest)",
        r"heart attack",
        r"(bleeding.*(won't|will not|cannot|can't) stop)",
        r"(severe bleeding|heavy bleeding|arterial bleeding|spurting blood)",
        r"(can't breathe|cannot breathe|unable to breathe|severe shortness of breath|choking|gasping)",
        r"(face droop|arm weakness|slurred speech|stroke)",
        r"(unconscious|passed out|fainted and not waking|seizure|convulsions)",
        r"(severe allergic reaction|anaphylaxis|throat swelling up|tongue swelling)",
        r"(head injury.*unconscious|skull fracture|severe burn|poisoning|snake bite)"
    ]
    if any(re.search(pat, q) for pat in emergency_patterns):
        action = "Call 112 or an ambulance immediately. Keep the patient completely still and resting."
        info = "The symptoms described point to a potentially life-threatening medical emergency requiring acute clinical intervention."
        precautions = [
            "Do NOT allow the person to walk, drive, or exert physical energy.",
            "Do NOT give solid foods or large volumes of water until evaluated by paramedics.",
            "Loosen tight clothing around the neck, chest, and waist."
        ]
        steps = [
            "Dial 112 (National Emergency Helpline) or 108 (Ambulance) right now.",
            "Make the person sit upright in a supported position (or recovery position if breathing but unconscious).",
            "Clearly communicate observed symptoms and past medical history to emergency dispatchers.",
            "Monitor breathing and pulse continuously until the ambulance arrives."
        ]
        meds = []

        if "bleeding" in q:
            action = "Call 112 or an ambulance immediately. Apply firm, continuous direct pressure with a clean cloth or sterile gauze."
            info = "Uncontrolled bleeding can rapidly lead to hypovolemic shock. Immediate manual pressure is crucial."
            precautions = [
                "Do NOT remove soaked dressings or cloths; add fresh absorbent cloths directly over them.",
                "Do NOT apply a makeshift tourniquet unless trained, as improper use can cause tissue damage.",
                "Do NOT take blood-thinning painkillers like Aspirin or Ibuprofen, which increase bleeding."
            ]
            meds = [
                {
                    "name": "Povidone-Iodine (Betadine 5% Solution / Ointment)",
                    "type": "Topical Antiseptic",
                    "dose": "Apply topically once bleeding stops",
                    "purpose": "Prevents wound infection and kills microbial pathogens",
                    "instructions": "Clean surrounding intact skin gently and cover with sterile dressing",
                    "warning": "Do not apply inside deep spurting wounds while bleeding is actively profuse."
                },
                {
                    "name": "Sterile Compression Gauze & Dressing",
                    "type": "First-Aid Supply",
                    "dose": "Multiple sterile gauze pads",
                    "purpose": "Direct mechanical hemostasis to arrest severe hemorrhage",
                    "instructions": "Press down firmly and continuously for at least 10-15 minutes without lifting",
                    "warning": "Do NOT remove soaked pads; layer new pads directly on top."
                },
                {
                    "name": "CONTRAINDICATED: Aspirin / Ibuprofen / Blood Thinners",
                    "type": "Avoid / Danger",
                    "dose": "0 mg - DO NOT TAKE",
                    "purpose": "Prevent worsening of internal or external bleeding",
                    "instructions": "Do not administer any NSAIDs or anticoagulants to an actively bleeding patient",
                    "warning": "Aspirin impairs platelet aggregation and can cause fatal blood loss."
                }
            ]
            steps = [
                "Dial 112 or 108 immediately.",
                "Press down firmly on the wound using a clean cloth, towel, or sterile gauze.",
                "Elevate the bleeding limb above heart level if no bone fracture is suspected.",
                "Keep the person lying flat and warm to prevent shock until help arrives."
            ]
        elif "chest" in q or "heart" in q or "sweat" in q:
            action = "Call 112 or an ambulance immediately. Make him sit and rest; loosen tight clothing."
            info = "Chest pain accompanied by heavy sweating is a classic clinical indicator of acute coronary syndrome or myocardial infarction."
            precautions = [
                "Do NOT let him walk around, climb stairs, or drive himself to the hospital.",
                "Do NOT ignore the pain hoping it will fade away.",
                "Do NOT administer heavy meals or caffeinated drinks."
            ]
            meds = [
                {
                    "name": "Aspirin (Dispirin / Ecosprin 300mg)",
                    "type": "Emergency First-Aid OTC",
                    "dose": "300 mg (1 tablet) or 4 chewable baby aspirins (75-81mg each)",
                    "purpose": "Antiplatelet agent: stops blood clot from growing in coronary arteries",
                    "instructions": "MUST BE CHEWED (not swallowed whole) immediately with a sip of water for rapid absorption",
                    "warning": "Do NOT give if patient is allergic to aspirin, has an active stomach ulcer, or has bleeding disorders."
                },
                {
                    "name": "Sorbitrate / Nitroglycerin 5mg (Sublingual)",
                    "type": "Prescription Only - Emergency",
                    "dose": "5 mg tablet placed under the tongue",
                    "purpose": "Coronary vasodilator to relieve cardiac angina chest pressure",
                    "instructions": "Place under tongue ONLY IF PREVIOUSLY PRESCRIBED by the patient's cardiologist for known heart disease",
                    "warning": "Never give another person's prescription. Do NOT give if blood pressure is dangerously low or if erectile dysfunction drugs were taken within 24-48 hours."
                }
            ]
            steps = [
                "Call 112 or an ambulance immediately.",
                "Place him in a comfortable semi-reclined seated position on the floor or firm chair.",
                "Loosen tight collar, belt, and shirt buttons.",
                "Tell the responders his exact symptoms, duration, and any known heart conditions.",
                "If conscious and non-allergic, give 1 chewable Aspirin 300mg to chew slowly."
            ]
        else:
            meds = [
                {
                    "name": "First-Aid Shock Management",
                    "type": "Emergency Protocol",
                    "dose": "Keep patient warm & resting",
                    "purpose": "Stabilize vitals until ambulance arrival",
                    "instructions": "Do not give oral medication if patient is drowsy, dizzy, or vomiting",
                    "warning": "Call 112 first before attempting any home interventions."
                }
            ]

        return {
            "level": "EMERGENCY",
            "summary": "Possible life-threatening emergency signs detected.",
            "immediate_action": action,
            "information": info,
            "precautions": precautions,
            "medications": meds,
            "next_steps": steps,
            "professional_help": "Emergency medical personnel and hospital emergency department required immediately. Do not delay.",
            "disclaimer": "Emergency guidance only, not a medical diagnosis. Call 112 immediately."
        }

    # 4. CAUTION Conditions (PPT: "Fever for 3 days with vomiting")
    caution_patterns = [
        r"(fever.*(3|three|several|few) days)",
        r"(fever.*vomit|vomit.*fever)",
        r"(vomiting.*unable to keep|persistent vomiting)",
        r"(high fever|fever > 102|fever over 102)",
        r"(deep cut|cut needing stitches|puncture wound)",
        r"(abdominal pain|stomach pain lasting|appendicitis)",
        r"(sprain|swollen ankle|unable to bear weight|possible fracture)",
        r"(animal bite|dog bite|cat scratch)",
        r"(persistent cough.*week|blood in phlegm)"
    ]
    if any(re.search(pat, q) for pat in caution_patterns):
        action = "Take oral rehydration solutions in small sips and schedule a medical consultation soon."
        info = "These symptoms suggest an infection, inflammatory condition, or acute illness that could deteriorate without clinical assessment."
        precautions = [
            "Avoid solid or oily heavy foods while vomiting persists.",
            "Do NOT self-prescribe unverified antibiotics or strong painkillers.",
            "Watch closely for signs of dehydration (sunken eyes, extreme thirst, dry mouth, dark urine)."
        ]
        meds = []
        steps = [
            "Administer Oral Rehydration Solution (ORS) or electrolyte water in small, frequent sips (5-10 ml every few minutes).",
            "Log body temperature every 4 hours using a digital thermometer.",
            "Apply lukewarm sponge compresses to the forehead and armpits if fever exceeds 101°F.",
            "Visit a physician, general hospital, or outpatient clinic within the day for clinical diagnostic tests."
        ]

        if "fever" in q and "vomit" in q:
            action = "Stay hydrated with small, frequent sips of electrolyte solution (ORS) and see a doctor soon."
            info = "A multi-day fever accompanied by vomiting carries a high risk of dehydration and electrolyte imbalance from viral or bacterial infections."
            precautions = [
                "Do NOT force heavy solid meals; stick to light clear fluids.",
                "Do NOT take non-steroidal anti-inflammatory drugs (NSAIDs like ibuprofen/Combiflam) on an empty irritated stomach.",
                "Do NOT delay medical evaluation if the patient becomes lethargic or confused."
            ]
            meds = [
                {
                    "name": "Oral Rehydration Salts (ORS / Electral W.H.O. formula)",
                    "type": "Essential OTC First-Aid",
                    "dose": "1 sachet dissolved in 1 liter clean drinking water",
                    "purpose": "Replenishes vital sodium, potassium, and glucose lost through vomiting",
                    "instructions": "Take in small, frequent sips (50–100 ml every 15–20 minutes). Do not chug in large amounts.",
                    "warning": "Prepare fresh daily. Discard unused solution after 24 hours."
                },
                {
                    "name": "Paracetamol / Acetaminophen (Crocin / Dolo 650mg / Calpol)",
                    "type": "OTC Antipyretic & Analgesic",
                    "dose": "500 mg - 650 mg every 6 to 8 hours as needed",
                    "purpose": "Controls high fever and body ache safely without irritating gastric mucosa",
                    "instructions": "Take with a few sips of ORS or after light toast/crackers",
                    "warning": "Do not exceed 3000 mg in 24 hours. Avoid combining multiple paracetamol-containing cold medicines."
                },
                {
                    "name": "Ondansetron (Emeset / Vomikind 4mg)",
                    "type": "Prescription Anti-emetic",
                    "dose": "4 mg tablet (as prescribed by doctor)",
                    "purpose": "Suppresses severe nausea and prevents repeated vomiting episodes",
                    "instructions": "Place on tongue 30 minutes before trying to take fluids or paracetamol",
                    "warning": "Use strictly under medical advice, especially in infants or children."
                },
                {
                    "name": "CONTRAINDICATED: Ibuprofen / Combiflam / Diclofenac",
                    "type": "Avoid / Warning",
                    "dose": "DO NOT TAKE",
                    "purpose": "Prevent severe gastric mucosal irritation and gastritis",
                    "instructions": "NSAIDs on an empty, vomiting stomach can cause severe stomach cramps or ulceration",
                    "warning": "Stick to Paracetamol for fever management while vomiting persists."
                }
            ]
            steps = [
                "Sip Oral Rehydration Salts (ORS) or coconut water slowly.",
                "Monitor temperature every 3-4 hours.",
                "Seek a formal clinical evaluation at a local medical center today for blood tests (e.g. CBC, dengue, typhoid screening).",
                "Go to the emergency department if vomiting prevents all fluid intake for over 12 hours."
            ]
        else:
            meds = [
                {
                    "name": "Paracetamol (Crocin 500mg)",
                    "type": "OTC Analgesic",
                    "dose": "500 mg every 6 hours",
                    "purpose": "Pain relief and low-grade fever reduction",
                    "instructions": "Take with water after food",
                    "warning": "Do not exceed 3g per day."
                },
                {
                    "name": "Oral Rehydration Salts (ORS)",
                    "type": "OTC Hydration",
                    "dose": "1 liter daily",
                    "purpose": "Maintains electrolyte balance during illness",
                    "instructions": "Sip throughout the day",
                    "warning": "Consult doctor if symptoms do not improve in 24 hours."
                }
            ]

        return {
            "level": "CAUTION",
            "summary": "Symptoms that may worsen if not properly monitored.",
            "immediate_action": action,
            "information": info,
            "precautions": precautions,
            "medications": meds,
            "next_steps": steps,
            "professional_help": "Consult a qualified medical doctor or visit a health clinic today for diagnostic examination.",
            "disclaimer": "General guidance only. Does not replace professional medical evaluation."
        }

    # 5. GENERAL Conditions (PPT: "I have a mild headache")
    return {
        "level": "GENERAL",
        "summary": "Minor, non-urgent concern identified.",
        "immediate_action": "Rest in a quiet, dimly lit space and drink a glass of fresh water.",
        "information": "Mild headaches and non-acute discomfort are commonly triggered by dehydration, eye strain, stress, or lack of adequate sleep.",
        "precautions": [
            "Avoid prolonged screen time (smartphones, laptops, TV).",
            "Avoid loud environments and harsh bright lights.",
            "Do NOT exceed recommended over-the-counter dosages if taking mild pain relievers."
        ],
        "medications": [
            {
                "name": "Paracetamol / Acetaminophen (Crocin 500mg / Dolo 650mg)",
                "type": "OTC Pain Reliever",
                "dose": "500 mg (1 tablet)",
                "purpose": "Relieves mild to moderate tension headaches and muscle tightness",
                "instructions": "Take with a full glass of water. Allow 30-45 minutes to take effect.",
                "warning": "Do not exceed 3000 mg in 24 hours. Avoid alcohol while taking paracetamol."
            },
            {
                "name": "Ibuprofen (Brufen 200mg - 400mg)",
                "type": "OTC Anti-inflammatory",
                "dose": "200 mg - 400 mg (1 tablet)",
                "purpose": "Alternative anti-inflammatory pain relief for throbbing headaches",
                "instructions": "Take ONLY AFTER FOOD or snacks with plenty of water",
                "warning": "Do not take on an empty stomach. Avoid if you have active gastric ulcers or kidney disease."
            },
            {
                "name": "Electrolyte Water / ORS",
                "type": "OTC Hydration",
                "dose": "1-2 glasses",
                "purpose": "Reverses dehydration-induced vascular headache",
                "instructions": "Drink cool or room temperature water in slow steady sips",
                "warning": "Avoid excess caffeine or energy drinks."
            }
        ],
        "next_steps": [
            "Hydrate adequately with 1-2 glasses of water.",
            "Rest or take a 20-30 minute nap in a cool, ventilated room.",
            "Apply a cold or warm compress across your forehead or back of the neck.",
            "Monitor your condition over the next few hours."
        ],
        "professional_help": "Consult a doctor if the headache suddenly becomes severe ('thunderclap'), persists for days, or is accompanied by stiff neck, confusion, or visual disturbance.",
        "disclaimer": "General guidance only, not a medical diagnosis. Consult a doctor if symptoms persist."
    }
