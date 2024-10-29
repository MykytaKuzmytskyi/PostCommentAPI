import logging

from googleapiclient import discovery

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=settings.PERSPECTIVE_API_KEY,
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
)


async def analyze_text_toxicity(text: str) -> bool:
    analyze_request = {
        "comment": {"text": text},
        "requestedAttributes": {"TOXICITY": {}},
    }

    response = client.comments().analyze(body=analyze_request).execute()
    toxicity_score = response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

    if toxicity_score < 0.2:
        logger.info(f"Text toxicity level: Low ({toxicity_score:.2f})")
    elif 0.2 <= toxicity_score < 0.5:
        logger.info(f"Text toxicity level: Medium ({toxicity_score:.2f})")
    else:
        logger.info(f"Text toxicity level: High ({toxicity_score:.2f})")

    return toxicity_score
