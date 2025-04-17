# Annotation Template

To change the annotation template in Zotero:
1. **navigate to the "Advanced" section of your Zotero setting**
2. **open the "Config Editor,"** 
3. **search for "annotations.noteTemplates"** 
- this will allow you to modify the existing templates for how your PDF annotations are added to notes, using basic HTML and variables within curly brackets.

```html
{{if color == '#f19837'}}
    <h3>{{tags}}</h3>
    <p>
        {{highlight}}<br/>
        {{citation}}<br/>
        {{comment}}
    </p>
{{endif}}
```

This code will export only Orange Highlights as below:
    
### Challenges with Dark Skin Tones

“Most of these systems work very efficient, however, there are some challenges related to the accuracy of results of facial recognition systems when tested on images of people with dark skin. As a matter of fact, various studies demonstrate higher accuracy when tested on data set with white skin personnel, while exhibit a much lesser accuracy when the same algorithms are tested on dataset of people with dark skin.”

(Farooq et al., 2021, p. 145109)

{Comments will be added if exists}