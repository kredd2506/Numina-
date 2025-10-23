const items = $input.all().map((item) => item.json);
const cleanedItems = items.map((item) => {
  let cleanedOutput = item.output.replace(/```json|```/g, "");
  let parsedOutput = JSON.parse(cleanedOutput);
  let isBill = Object.keys(parsedOutput.bill).length !== 0 ? "1" : "0";
  let isInvoice = Object.keys(parsedOutput.invoice).length !== 0 ? "1" : "0";
  return { isBill, isInvoice };
});
return cleanedItems;
