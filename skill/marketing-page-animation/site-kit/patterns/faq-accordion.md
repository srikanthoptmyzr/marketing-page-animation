# FAQ accordion: `c-faq-section`

Status: **observed**.

- Section background `bg-[#F0EFEF]`, bottom padding `pb-[130px] md:pb-[264px]` (the extra space hosts the footer overlap); inner width `lg:w-[890px]`; each item in a white card `rounded-[12px] shadow-sm`.
- Heading: H2 "Frequently Asked Questions (FAQs)"; some pages use an H1 such as "PPC Monitoring FAQs". Keep one H1 per page.
- Item markup:
```html
<div class="faq-item" onclick="toggleFaq(this)">
  <button class="flex justify-between items-center w-full text-left">
    <span class="text-desktopSubHeadingsP4 md:text-desktopSubHeadingsP3 font-medium">Question</span>
    <svg><!-- chevron, stroke #626C7A, rotates 180deg when open --></svg>
  </button>
  <div class="faq-content overflow-hidden" style="height: 0">
    <p class="text-mobileBodyB5 md:text-desktopSubHeadingsP5 text-colorSurfaceDarkNormal pt-[12px] lg:w-10/12">Answer</p>
  </div>
  <hr class="border-gray-200">
</div>
```
- Behavior: click toggles height (0 to content height) and rotates the chevron.
- **Dev note:** the site uses an inline `onclick="toggleFaq(this)"`. New pages should reuse the site's existing `toggleFaq` function and markup so behavior stays identical; flag to the dev team that the inline handler conflicts with the Marketing-OS guidance on inline handlers.
- Content rules: 6 to 9 questions; questions are plain sentences; answers 1 to 3 short paragraphs; all copy is translatable content, none hard-coded.
