# Dive Site Documentation Template

**Purpose**: This template provides a standardized structure for documenting dive sites. It ensures consistency, completeness, and RAG-friendly content that helps divers discover and plan dives effectively.

---

## Frontmatter (Required YAML Metadata)

```yaml
---
doc_type: 'dive_site'
site_id: '[unique-identifier-kebab-case]'
title: '[Site Name]'
destination: '[Location, Country/Region]'
min_certification: 'OW|AOW|Rescue|DM|Technical'
difficulty: 'beginner|intermediate|advanced|expert'
depth_range_m: [min_depth, max_depth]
tags: ['tag1', 'tag2', 'tag3']
keywords: ['keyword1', 'keyword2', 'keyword3']
last_updated: 'YYYY-MM-DD'
data_quality: 'compiled|verified|operator-provided|community-sourced'
sources:
  - 'Source 1 URL or citation'
  - 'Source 2 URL or citation'
---
```

**Field Descriptions:**

- `doc_type`: Always "dive_site" (enables filtering in RAG)
- `site_id`: Unique identifier (e.g., "bali-uss-liberty")
- `title`: Common site name
- `destination`: Location (e.g., "Bali, Indonesia")
- `min_certification`: Minimum required certification level
- `difficulty`: Overall difficulty assessment
- `depth_range_m`: [minimum, maximum] depths in meters
- `tags`: Searchable characteristics (wreck, wall, drift, reef, etc.)
- `keywords`: Natural language search terms
- `last_updated`: Date of last content update
- `data_quality`: Source confidence level
- `sources`: References for verification

---

## Section 1: Quick Facts

**Purpose**: Provide at-a-glance critical information for dive planning.

**Format**: Table

```markdown
## 1. Quick Facts

| Feature         | Details                              |
| :-------------- | :----------------------------------- |
| **Depth Range** | X–Y m                                |
| **Visibility**  | X–Y m (typical range)                |
| **Current**     | None/Gentle/Moderate/Strong/Variable |
| **Water Temp**  | X–Y °C (seasonal range)              |
| **Season**      | Best: [months]; Diveable: [months]   |
```

**RAG Tip**: Use natural language in the "Details" column (e.g., "10–30 m, best visibility March–May").

---

## Section 2: Site Overview

**Purpose**: Provide compelling narrative context that answers "Why dive here?"

**Format**: Prose (3-5 paragraphs)

```markdown
## 2. Site Overview

[Opening paragraph: Location, key attraction, what makes it special]

- **Known for:** [3-5 signature features or highlights]
- **Atmosphere:** [Describe the feel/vibe of the dive]
- **Why dive here:** [Unique selling points, what divers gain from this site]
```

**RAG Optimization:**

- Use conversational language: "If you want to see sharks, this is the place..."
- Answer implicit questions: "Is this site good for beginners?" → "This site is ideal for new divers..."
- Include comparisons: "Unlike other wrecks, this one is fully penetrable..."

**Example:**

```markdown
Tiger Reef is a submerged pinnacle located between Labas Island and Sepoi Island off Tioman's east coast. The site takes its name from its shape—when viewed from above, the rock formation resembles a crouching tiger. This is one of Tioman's flagship dive sites, known for dramatic boulder formations, prolific soft coral coverage, and predictable encounters with large pelagic schooling fish.

- **Known for:** Explosive coral-covered pinnacle, large schools of jacks and barracudas, strong currents that attract pelagic life
- **Atmosphere:** Energetic and action-packed, especially when pelagics are present
- **Why dive here:** Combines vibrant coral aesthetics with reliable macro critter life and the thrill of encountering large schooling fish
```

---

## Section 3: Underwater Topography

**Purpose**: Help divers visualize the site structure and key features.

**Format**: Bullet list with detailed descriptions

```markdown
## 3. Underwater Topography

- **Reef type:** [Reef/Wall/Wreck/Pinnacle/Boulder/Cave/etc. with detail]
- **Depth contour:** [Describe depth profile and slope]
- **Specific features:**
  - [Feature 1: swim-throughs, caverns, canyons, cleaning stations]
  - [Feature 2: coral gardens, wreck sections, artifacts]
  - [Feature 3: overhangs, ledges, sand patches]
- **Key structures:** [Main focal points or landmarks for navigation]
```

**RAG Optimization:**

- Use descriptive language: "massive boulders stacked like a fortress"
- Include visual metaphors: "resembles Swiss cheese with interconnected passages"
- Mention navigation aids: "the anchor sits at 12m on the main pinnacle"

---

## Section 4: Typical Dive Profile

**Purpose**: Provide practical dive planning information.

**Format**: Structured bullet list

```markdown
## 4. Typical Dive Profile

- **Entry method:** [Boat/shore, negative/positive descent, anchor line, etc.]
- **Route:** [Typical navigation path or circuit]
- **Typical depth range:** [Most common working depth]
- **Max recommended depth:** [Conservative maximum]
- **Style:** [Drift/stationary, exploration/relaxed, penetration/external]
- **Duration:** [Typical bottom time]
- **Turnaround:** [When/why divers typically turn around]
```

**RAG Optimization:**

- Answer "How long can I dive here?" explicitly
- Include air consumption notes: "Current increases air consumption by 20-30%"
- Mention certification relevance: "Stay above 18m if you're Open Water certified"

---

## Section 5: Marine Life

**Purpose**: Set expectations for wildlife encounters.

**Format**: Categorized lists with seasonal notes

```markdown
## 5. Marine Life

- **Common species (seen on most dives):**
  - [Species 1]
  - [Species 2]
  - [Species 3]

- **Occasional species (regularly but not guaranteed):**
  - [Species 1]
  - [Species 2]

- **Rare encounters:**
  - [Species 1] (conditions: [when/why])
  - [Species 2] (conditions: [when/why])

- **Seasonal highlights:**
  - **[Month range]:** [What's special during this period]
  - **[Month range]:** [What's special during this period]
```

**RAG Optimization:**

- Use natural language: "You'll almost certainly see barracuda schools"
- Answer likelihood: "Sharks are seen on about 30% of dives"
- Include behaviors: "Manta rays visit cleaning stations from June-September"

**Example Q&A Enhancement (optional subsection):**

```markdown
### Common Questions About Marine Life

**Q: Will I see sharks?**
A: Black-tip reef sharks are occasionally spotted resting under ledges, seen on approximately 20-30% of dives.

**Q: When is the best time for pelagics?**
A: March–May and September–October offer the highest probability of encountering large schools of jacks and barracudas.
```

---

## Section 6: Conditions

**Purpose**: Help divers assess suitability and prepare appropriately.

**Format**: Detailed bullet list with seasonal notes

```markdown
## 6. Conditions

- **Visibility:** [Range with seasonal variations]
- **Current:** [Strength, direction, predictability, tidal influence]
- **Surge/Swell:** [Exposure level, depth-dependent effects]
- **Temperature:** [Range with seasonal notes]
- **Triggers:** [What causes condition changes: tides, monsoon, etc.]
```

**RAG Optimization:**

- Be specific: "Visibility averages 20m in March, drops to 10m in August"
- Warn about risks: "Strong downcurrents possible during spring tides"
- Help with planning: "Dive at slack tide for minimal current"

---

## Section 7: Difficulty Assessment

**Purpose**: Help divers self-assess if the site matches their skill level.

**Format**: Categorized lists with clear skill requirements

```markdown
## 7. Difficulty Assessment

- **Skills required:**
  - [Skill 1: e.g., advanced buoyancy control]
  - [Skill 2: e.g., comfortable in strong current]
  - [Skill 3: e.g., wreck penetration training]

- **Challenges:**
  - **[Challenge 1]:** [Description and why it's challenging]
  - **[Challenge 2]:** [Description and mitigation strategies]

- **Beginner notes:**
  - [Specific guidance for less experienced divers]
  - [Conditions when beginners can attempt this site]

- **Advanced notes:**
  - [What advanced divers will appreciate]
  - [Technical diving opportunities if applicable]
```

**RAG Optimization:**

- Use certification language: "Requires Advanced Open Water due to depth and current"
- Include dive count guidance: "Recommended 20+ dives before attempting"
- Answer "Can I do this dive?" directly: "Not suitable for divers with fewer than 15 dives"

---

## Section 8: Recommended Diver Profile

**Purpose**: Clear guidance on who should dive this site.

**Format**: Structured criteria

```markdown
## 8. Recommended Diver Profile

- **Certification:** [Minimum cert level + reasoning]
- **Min dive count:** [Recommended experience level]
- **Comfort level:**
  - [Comfort requirement 1]
  - [Comfort requirement 2]
  - [Comfort requirement 3]
```

**Example:**

```markdown
- **Certification:** Advanced Open Water Diver (AOWD) or equivalent
- **Min dive count:** 20–50 dives recommended
- **Comfort level:**
  - Comfortable handling moderate-to-strong current
  - Comfortable with depths 20+ m
  - Able to navigate complex 3D terrain
```

---

## Section 9: Hazards & Safety Notes

**Purpose**: Ensure diver safety through clear risk communication.

**Format**: Categorized hazards with mitigation strategies

```markdown
## 9. Hazards & Safety Notes

- **Physical hazards:**
  - **[Hazard 1]:** [Description, likelihood, mitigation]
  - **[Hazard 2]:** [Description, likelihood, mitigation]

- **Depth risks:**
  - [Narcosis, decompression, overhead environment]

- **Surface risks:**
  - [Boat traffic, surface conditions, exit challenges]

- **Environmental risks:**
  - [Surge, thermoclines, low visibility]

- **Other hazards:**
  - [Wildlife (lionfish, jellyfish), sharp objects, entanglement]

- **Incidents:** [Known incident history or "No major incidents documented"]
```

**RAG Optimization:**

- Be direct: "Stonefish are camouflaged on the reef—never touch anything"
- Provide context: "Current can separate buddy teams—maintain visual contact"
- Include statistics if available: "Incidents are rare; professional operators have excellent safety records"

---

## Section 10: Photography Notes

**Purpose**: Help photographers plan their equipment and approach.

**Format**: Technical guidance with practical tips

```markdown
## 10. Photography Notes

- **Lens recommendation:** [Macro/wide-angle/both with specific focal lengths]
- **Focal length:**
  - **Macro:** [X-Y mm for specific subjects]
  - **Wide-angle:** [X-Y mm for specific subjects]
- **Lighting:**
  - [Strobe requirements, ambient light viability, backscatter risks]

- **Subject tips:**
  - [Best subjects and how to approach them]
  - [Composition opportunities]
  - [Behavioral notes for critters]

- **Best time:** [Optimal season/time of day for photography]
- **Challenges:** [Current, particulate matter, skittish subjects]
```

**RAG Optimization:**

- Answer gear questions: "A 60mm macro lens is ideal for nudibranchs"
- Include settings guidance: "Use ISO 400 and f/8 for reef scenes in good visibility"

---

## Section 11: Best Time to Dive

**Purpose**: Help divers choose optimal timing for their visit.

**Format**: Seasonal breakdown with detailed reasoning

```markdown
## 11. Best Time to Dive

- **High season:** [Month range]
  - **Why:** [Visibility, weather, marine life, water temp]
  - **Pros:** [List advantages]
  - **Cons:** [Any drawbacks, e.g., crowds]

- **Shoulder season:** [Month range]
  - **Conditions:** [What to expect]
  - **Trade-offs:** [Pros and cons]

- **Low season:** [Month range]
  - **What typically goes wrong:** [Weather, visibility, closures]
  - **Not recommended:** [Clear guidance if applicable]

- **Monthly notes:**
  - **[Month]:** [Brief condition summary]
  - **[Month]:** [Brief condition summary]
```

**RAG Optimization:**

- Use natural language: "March to May is the sweet spot—excellent visibility and calm seas"
- Answer "When should I go?" directly
- Include booking advice: "Book 3-6 months ahead for high season"

---

## Section 12: Practical Tips

**Purpose**: Insider knowledge for a better dive experience.

**Format**: Actionable advice list

```markdown
## 12. Practical Tips

- **Timing:** [Best time of day, tidal considerations]
- **Frequency:** [How often this site is dived, availability]
- **Cancellations:** [Common reasons dives are canceled]
- **Gas choice:** [Air vs nitrox recommendations]
- **Exposure protection:** [Wetsuit thickness, hood, gloves]
- **Other tips:**
  - [Tip 1: booking, fees, permits]
  - [Tip 2: what to bring, what to leave]
  - [Tip 3: local etiquette or customs]
```

**RAG Optimization:**

- Be specific: "Dive this site in the morning (08:00-11:00) when current is calmest"
- Answer cost questions: "Site fees are $5 per diver, included in most packages"
- Local knowledge: "Ask your operator about the best entry point based on current direction"

---

## Section 13: Example Dive Narrative (Optional but Highly Recommended)

**Purpose**: Bring the site to life through storytelling. This is excellent for RAG semantic matching.

**Format**: First-person or second-person narrative (300-500 words)

```markdown
## 13. Example Dive Narrative

[Write an immersive, descriptive account of a typical dive at this site. Include sensory details, emotions, and specific moments. This helps RAG match on "what's it like to dive here?" type queries.]

Example opening:
"You step back from the boat rail, regulator in, and descend the anchor line into a haze of blue. Current is moderate today—noticeable but manageable..."
```

**RAG Optimization:**

- Use vivid, sensory language
- Include emotions and reactions: "You can't help but grin when..."
- Mention specific moments: "Twenty minutes in, a wall of jacks suddenly appears..."
- This section is gold for matching conversational queries like "What's it like diving at X?"

---

## Section 14: Keywords & Tags

**Purpose**: Enhance searchability and RAG retrieval.

**Format**: Categorized keyword lists

```markdown
## 14. Keywords & Tags

- **Keywords:**
  - [Site name]
  - [Location variants]
  - [Key features]
  - [Marine life highlights]
  - [Dive type descriptors]
- **Categories:**
  - **Depth:** [beginner/intermediate/advanced + range]
  - **Difficulty:** [skill level + primary challenges]
  - **Type:** [reef/wreck/wall/pinnacle/etc.]
  - **Marine life focus:** [What divers come here to see]
  - **Activity:** [recreational/technical/photography/training]
```

**RAG Optimization:**

- Include common misspellings or alternate names
- Add comparative terms: "similar to [other famous site]"
- Include question keywords: "best dive site for beginners in [region]"

---

## Section 15: Source Notes (Internal Use)

**Purpose**: Document research provenance and data quality for future updates.

**Format**: Detailed citation and verification log

```markdown
## 15. Source Notes (Internal)

- **Sources:**
  1. [Source 1 with URL and date accessed]
  2. [Source 2 with URL and date accessed]
  3. [etc.]

- **Verification notes:**
  1. **Depth range:** [How verified, any discrepancies between sources]
  2. **Current:** [Consistency across sources, any conflicting info]
  3. **Marine life:** [Cross-reference notes, seasonal confirmations]
- **Inferences:**
  1. [What was inferred vs. directly stated]
  2. [Assumptions made and reasoning]
- **Gaps and uncertainties:**
  1. [Missing information]
  2. [Conflicting data that needs resolution]
  3. [Areas requiring field verification]
```

---

## Content Writing Guidelines for RAG Optimization

### 1. Use Natural, Conversational Language

- Write as if answering a friend's question
- Use "you" and "your" to address the reader
- Include rhetorical questions: "Want to see sharks? This is the spot."

### 2. Answer Implicit Questions

Common diver questions to address throughout:

- Is this suitable for my level?
- What will I see?
- When should I go?
- How much does it cost?
- Is it safe?
- What equipment do I need?
- How do I get there?

### 3. Include Comparison Language

- "Unlike [other site], this one has..."
- "If you enjoyed [famous site], you'll love this"
- "This is the [region's] equivalent of [famous site]"

### 4. Add Q&A Sections Where Helpful

Explicitly format common questions:

```markdown
### Common Questions

**Q: Can beginners dive here?**
A: Yes, but only with a guide and in calm conditions...

**Q: How likely am I to see manta rays?**
A: During manta season (June-Sept), sightings occur on 60-80% of dives...
```

### 5. Use Specific Numbers and Facts

- "Visibility averages 25m in March" (not "good visibility")
- "Seen on 70% of dives" (not "commonly seen")
- "Requires 20+ logged dives" (not "experienced divers")

### 6. Include Seasonal Specificity

- Monthly breakdowns are better than "winter/summer"
- Explain WHY conditions change: "March-May offers best visibility because..."

### 7. Address Multiple Skill Levels

- Explicitly state beginner/intermediate/advanced guidance
- "If you're new to diving..." vs "Advanced divers can explore..."

### 8. Use Section Headings as Natural Questions

Instead of "Conditions" use "What are the water conditions like?"
Instead of "Marine Life" use "What will I see underwater?"

---

## Metadata Completeness Checklist

Before publishing, ensure:

- [ ] All frontmatter fields completed
- [ ] At least 2 reliable sources cited
- [ ] Depth range matches between metadata and content
- [ ] Seasonal information included
- [ ] Difficulty assessment matches certification requirement
- [ ] Safety hazards documented
- [ ] At least 10 keywords for searchability
- [ ] Last updated date is current
- [ ] Source verification notes completed
- [ ] At least one Q&A or narrative section included

---

## Example Shortened Dive Site (For Quick Reference)

See `tioman-tiger-reef.md` for a full implementation of this template.

For sites with limited information, prioritize:

1. Quick Facts (Section 1)
2. Site Overview (Section 2)
3. Marine Life (Section 5)
4. Difficulty Assessment (Section 7)
5. Best Time to Dive (Section 11)

Remaining sections can be added as information becomes available.

---

**Template Version**: 1.0  
**Last Updated**: 2026-01-01  
**Maintained By**: DovvyBuddy Content Team
