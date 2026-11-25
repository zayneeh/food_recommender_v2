const form = document.querySelector('#pantry');
const results = document.querySelector('#results');
const message = document.querySelector('#message');
const button = document.querySelector('#submit');
function node(tag, text, cls) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (cls) element.className = cls;
  return element;
}
function render(recipe) {
  const card = node('article');
  const header = node('div', undefined, 'row');
  header.append(node('h3', recipe.name), node('span', recipe.can_make ? 'All required ingredients matched' : `${recipe.missing_ingredients.length} missing`, recipe.can_make ? 'status complete' : 'status missing'));
  const coverage = node('progress'); coverage.max = 1; coverage.value = recipe.coverage;
  coverage.setAttribute('aria-label', 'Recipe ingredient coverage');
  card.append(header, coverage, node('small', `${Math.round(recipe.coverage * 100)}% of required ingredient groups matched`),
    node('p', `You have: ${recipe.used_ingredients.join(', ')}`),
    node('p', `Still need: ${recipe.missing_ingredients.join(', ') || 'None in the matching data'}`));
  if (recipe.optional_missing.length) card.append(node('p', `Optional: ${recipe.optional_missing.join(', ')}`, 'muted'));
  const details = node('details');
  details.append(node('summary', 'View original recipe'),node('h4','Ingredients'),node('pre',recipe.original_ingredients),node('h4','Instructions'),node('pre',recipe.instructions));
  card.append(details); return card;
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  results.replaceChildren(); button.disabled = true; message.textContent = 'Finding recipes…';
  try {
    const response = await fetch('/api/recommend', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ingredients:document.querySelector('#ingredients').value,assume_water:document.querySelector('#water').checked,min_match:Number(document.querySelector('#threshold').value)})});
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const {recipes} = await response.json();
    message.textContent = recipes.length ? `${recipes.length} matches shown, ordered by fewest missing ingredients.` : 'No matching recipes. Try adding more ingredients or lowering the minimum coverage.';
    for (const recipe of recipes) results.append(render(recipe));
  } catch(error) { message.textContent = `Could not load recommendations: ${error.message}`; }
  finally { button.disabled = false; }
});
