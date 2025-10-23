const out = [];
for (const item of items) {
  const b = item.binary?.file;
  if (b) {
    const name = (b.fileName || '').toLowerCase();
    if (!b.mimeType) {
      b.mimeType = name.endsWith('.png') ? 'image/png'
               : name.endsWith('.jpg') || name.endsWith('.jpeg') ? 'image/jpeg'
               : name.endsWith('.pdf') ? 'application/pdf'
               : 'application/octet-stream';
    }
  }
  out.push(item);
}
return out;
