// Detect qualifying attachments & split into:
//  - one "control" item: kind="control", hasOcrAttachment: boolean
//  - N "attachment" items: kind="attachment", with binary.file ready for S3

function guessMimeFromName(name='') {
  const n = name.toLowerCase();
  if (n.endsWith('.png')) return 'image/png';
  if (n.endsWith('.jpg') || n.endsWith('.jpeg')) return 'image/jpeg';
  if (n.endsWith('.pdf')) return 'application/pdf';
  return 'application/octet-stream';
}
function cleanSubject(item) {
  // Prefer parsed subject; fallback to header with "Subject: " stripped
  const parsed = item.json.subject;
  if (parsed) return parsed;
  const hdr = item.json.headers?.subject || '';
  return hdr.replace(/^Subject:\s*/i, '');
}

const item = items[0];
const bin = item.binary || {};
const attachments = Object.entries(bin).filter(([k, v]) => {
  const mt = (v.mimeType || '').toLowerCase();
  const fn = (v.fileName || '').toLowerCase();
  return mt.startsWith('image/') || fn.endsWith('.pdf');
});

const subject = cleanSubject(item);
const out = [];

// CONTROL item (only one)
out.push({
  json: {
    kind: 'control',
    hasOcrAttachment: attachments.length > 0,
    subject,
    html: item.json.html,
    text: item.json.text,
    messageId: item.json.id,
    headers: item.json.headers,   // keep original header block if you need it
  },
  binary: item.binary,            // optional: keep raw binaries for reference
});

// ATTACHMENT items (one per qualifying attachment)
for (const [name, data] of attachments) {
  const fileName = data.fileName || name;
  const mimeType = data.mimeType || guessMimeFromName(fileName);
  const normalized = { ...data, mimeType, fileName };

  out.push({
    json: {
      kind: 'attachment',
      hasOcrAttachment: true,
      fileName,
      messageId: item.json.id,
      subject,
      html: item.json.html,
      text: item.json.text,
      attachmentProperty: name, // original property name (attachment_0, etc.)
    },
    binary: { file: normalized }, // S3 node will read from binary.file
  });
}

return out;
