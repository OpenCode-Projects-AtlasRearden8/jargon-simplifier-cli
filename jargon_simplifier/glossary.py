"""Built-in jargon glossaries for the plain-English rewriter.

Each entry maps a term to a tuple of:

    (plain English swap, short definition)

Jargon is tagged by domain: "legal" and "medical-admin" terms lean toward
those audiences; "phrasing" entries are stiff openers worth deleting outright.

No replacement invents information - a swap re-words what is already there.
"""

GLOSSARY: dict[str, tuple[str, str]] = {
    # ---------------------------------------------------------------- legal
    "pursuant to": ("under", "Complying with or as required by."),
    "hereinafter": ("from now on", "The document will use this shorter name later."),
    "the undersigned": ("I", "The person who signed this."),
    "aforementioned": ("the same", "Already named above in this document."),
    "prior to": ("before", "Earlier than."),
    "subsequent to": ("after", "Later than."),
    "in the event that": ("if", "When something happens."),
    "heretofore": ("until now", "Up to this point."),
    "herewith": ("with this", "Included with this document."),
    "theretofore": ("before that", "Before that point in time."),
    "notwithstanding": ("despite", "Even though this is true."),
    "whereas": ("while it is true that", "Because this is true."),
    "covenant and agree": ("agree", "Formally promise."),
    "mutual agreement": ("everyone agreed", "All parties accepted the same deal."),
    "demand letter": ("formal request for payment", "A letter asking for money owed, before a lawsuit."),
    "time is of the essence": ("deadlines matter here", "You must meet the exact deadline or risk breaking the contract."),
    "waives": ("gives up", "You choose not to use a right you had."),
    "liability": ("legal responsibility", "Who has to answer or pay when something goes wrong."),
    "indemnify": ("cover the cost of harm", "One side promises to repay the other for damage or claims."),
    "severability": ("parts survive on their own", "If one part of a deal is thrown out, the rest still stands."),
    "force majeure": ("events nobody can control", "Unforeseeable disasters like fires or wars that excuse delays."),
    "arbitration": ("private decision instead of court", "A neutral person decides a dispute without a judge."),
    "breach": ("broken promise", "Failing to do what was promised."),
    "estimated": ("about", "A close guess rather than a fixed promise."),
    "shall": ("must", "You are required to."),
    # ------------------------------------------------------- medical admin
    "adverse event": ("bad side effect", "Harm caused by a treatment or medication."),
    "concomitant": ("taken at the same time", "Using two things together, like two medicines."),
    "prior to discharge": ("before leaving", "Earlier than when a patient goes home."),
    "discharge summary": ("leaving-papers notes", "The doctor's summary written when a patient goes home."),
    "treatment protocol": ("care plan", "The standard plan for treating a condition."),
    "pre-authorization": ("insurance approval first", "Your insurer must approve a treatment before you get it."),
    "itemized bill": ("line-by-line bill", "A bill that lists every charge separately."),
    "copayment": ("fixed share you pay", "The set amount you pay for each visit."),
    "deductible": ("amount you pay first", "What you pay out of pocket before insurance starts paying."),
    "out-of-pocket maximum": ("yearly payment cap", "The most you can pay in a year before insurance covers the rest."),
    "explanation of benefits": ("insurance payment summary", "A letter showing what insurance covered and what you owe."),
    "prn": ("as needed", "Take or use only when needed."),
    "npo": ("nothing by mouth", "Do not eat or drink anything."),
    "bid": ("twice a day", "Take the dose two times per day."),
    "tid": ("three times a day", "Take the dose three times per day."),
    "acute": ("sudden and severe", "Comes on fast and needs quick care."),
    "chronic": ("long-lasting", "Stays with you for months or years."),
    "benign": ("not cancer", "Growth that does not spread or cause cancer."),
    "contraindicated": ("should not be used", "A reason to avoid this treatment."),
    "intervention": ("treatment", "The action taken to fix the problem."),
    "comorbidity": ("other condition at the same time", "A second illness someone has alongside the first."),
    "ambulatory": ("able to walk", "Well enough to walk and move around."),
    "prior authorization": ("insurance approval first", "Your insurer must approve a treatment before you get it."),
    "referral": ("recommendation to a specialist", "Your provider sends you to a specialist for more care."),
    # ------------------------------------------------------ plain business
    "utilize": ("use", "A stiff way to say use."),
    "commence": ("start", "Begin."),
    "terminate": ("end", "Stop or cancel."),
    "endeavor": ("try", "Attempt."),
    "obligated": ("required", "Must do it."),
    "expeditiously": ("quickly", "Fast and without delay."),
    "facilitate": ("help", "Make something easier."),
    "sufficient": ("enough", "As much as needed."),
    "commencing on": ("starting on", "The date when something begins."),
    "due and owing": ("still owed", "Money that has not been paid."),
    "hereby": ("by this", "Done with these words in the document."),
    "herein": ("in this", "Inside this document."),
    "wherefore": ("so", "For these reasons."),
    "in lieu of": ("instead of", "In place of something."),
    "in excess of": ("more than", "A bigger amount than."),
    "per annum": ("per year", "Every year."),
    "verbatim": ("word for word", "Exactly as it was said or written."),
    # ----------------------------------------------------- stiff phrasing
    "please be advised that": ("", "Stiff opener that adds nothing."),
    "Please be advised that": ("", "Stiff opener that adds nothing."),
    "we are writing to inform you that": ("", "Stiff opener that adds nothing."),
    "We are writing to inform you that": ("", "Stiff opener that adds nothing."),
    "kindly note that": ("", "Stiff filler phrase."),
    "please note that": ("Please note: ", "Slightly stiff setup phrase."),
    "in the neighborhood of": ("about", "Around that amount."),
    "at your earliest convenience": ("as soon as you can", "Whenever next is possible."),
    "enclosed please find": ("I have included", "This document is attached here."),
    "aforethought": ("planned ahead", "Thought out in advance."),
}

LEGAL_TERMS = [
    "pursuant to", "hereinafter", "the undersigned", "aforementioned", "prior to",
    "subsequent to", "in the event that", "heretofore", "herewith", "theretofore",
    "notwithstanding", "whereas", "covenant and agree", "mutual agreement",
    "demand letter", "time is of the essence", "waives", "liability", "indemnify",
    "severability", "force majeure", "arbitration", "breach", "shall", "hereby",
    "herein", "wherefore", "in lieu of", "in excess of", "per annum",
    "due and owing", "aforethought", "estimated",
]

MEDICAL_TERMS = [
    "adverse event", "concomitant", "prior to discharge", "discharge summary",
    "treatment protocol", "pre-authorization", "itemized bill", "copayment",
    "deductible", "out-of-pocket maximum", "explanation of benefits", "prn",
    "npo", "bid", "tid", "acute", "chronic", "benign", "contraindicated",
    "intervention", "comorbidity", "ambulatory", "prior authorization",
    "referral", "prior to",
]

PHRASING_TERMS = [
    "please be advised that", "Please be advised that",
    "we are writing to inform you that", "We are writing to inform you that",
    "kindly note that", "please note that", "at your earliest convenience",
    "enclosed please find", "in the neighborhood of",
]
