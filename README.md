# HighlightHero

![HighlightHero](https://github.com/user-attachments/assets/2e9ac83e-0d86-4d51-948d-9e121016688d)

## Inspiration
As frequent Instagram doomscrollers, we often came across players' sports highlights on our feeds. However, we were dismayed at the lack of quality in many of the videos we saw. This sparked our motivation to revolutionize the way players showcase their favorite clips.

## What it does
HighlightHero allows players or parents to upload a full game video and receive only the most exciting and interesting parts as highlights. The platform goes a step further by integrating AI-generated narration and background music that dynamically change based on the intensity and context of the gameplay (e.g., more exciting clips will feature more intense music and commentary).

## How we built it
- **Frontend:** Built using React for a responsive and user-friendly interface.
- **Backend:** Powered by Flask and integrated with:
  - **Quen2** for video segmentation.
  - **OpenAI** for natural language processing to extract descriptions.
  - **11labs** for contextual commentary generation.
  - **Suno** for AI-generated music that enhances the highlight reel.

## Challenges we ran into
Identifying highlights in a full-length game was a significant challenge. Our solution was to break the game into defined subsections, extract descriptions from these subsections, and use those descriptions to identify and rank the most interesting parts of the game. This approach allowed us to automate the process of identifying highlights based on dynamic events in the video.

## Accomplishments that we're proud of
Apart from technical milestones, one of our teammates impressively finished a whole crate of Soylent in just one hour!

## What we learned
This project imparted us with valuable technical skills, reinforced the importance of teamwork, and taught us a crucial lesson: "When there's a will, there's a way."

## What's next for HighlightHero
We originally envisioned incorporating a stable diffusion overlay onto the generated highlights to enhance the visuals even further. Although we ran out of time to implement this feature, it remains a high-priority addition for future iterations of the project.

## Getting Started

To run this project locally, follow these instructions:

### Prerequisites
- Node.js
- Python 3.x
- Flask
- React.js

### Installation
1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/HighlightHero.git
   cd HighlightHero
