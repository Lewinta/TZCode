#!/home/tzcode/.nvm/versions/node/v16.15.0/bin/node

// const forge = require('node-forge'); // npm install node-forge
// const xmldom = require('xmldom'); // npm install xmldom

// class FirmaXMLService {
//     constructor() {}

//     // Method to digitally sign an XML
//     Firmar(xml, certifado, password) {
//         let pem = this.convertToPem(certifado, password);
//         let privateKey = forge.pki.privateKeyFromPem(pem.pemKey);

//         let md = forge.md.sha256.create();
//         var xmlData2 = new xmldom.DOMParser().parseFromString(xml);
//         var xmlCanolizadoData2 = this.c14nCanonicalization(xmlData2.firstChild, null);
//         md.update(xmlCanolizadoData2.toString(), 'utf8');

//         let messageDigest = forge.util.encode64(md.digest().data);

//         let pemXMLFormat = this.obtenerPEMXMLFormat(pem.pemCertificate);
//         let xmlSinFirmado = this.agregarEstructuraFirma(
//             xmlCanolizadoData2.toString(),
//             pemXMLFormat,
//             messageDigest
//         );

//         var xmlData = new xmldom.DOMParser().parseFromString(xmlSinFirmado);
//         var xmlCanolizado = this.c14nCanonicalization(
//             xmlData.getElementsByTagName("SignedInfo")[0],
//             { defaultNsForPrefix: { ds: 'http://www.w3.org/2000/09/xmldsig#' } }
//         );

//         md = forge.md.sha256.create();
//         md.update(xmlCanolizado.toString(), 'utf8');
//         let signature = privateKey.sign(md);

//         let signatureValue =
//             '<SignatureValue>' + forge.util.encode64(signature) + '</SignatureValue>';
//         let indiceFirma = xmlSinFirmado.search('</Signature>');
//         let xmlFirmado =
//             xmlSinFirmado.substring(0, indiceFirma) +
//             signatureValue +
//             xmlSinFirmado.substring(indiceFirma);

//         return {
//             xmlFirmadoString: xmlFirmado,
//             xmlFirmadoBlob: this.generarBlobArchivoFirmado(xmlFirmado),
//         };
//     }

//     generarBlobArchivoFirmado(xmlFirmado) {
//         return new Blob([xmlFirmado], { type: "text/xml;charset=utf-8" });
//     }

//     obtenerPEMXMLFormat(PEM) {
//         let PEMToXmlFormat = PEM.replace('-----BEGIN CERTIFICATE-----', '');
//         PEMToXmlFormat = PEMToXmlFormat.replace('-----END CERTIFICATE-----', '');
//         return PEMToXmlFormat;
//     }

//     agregarEstructuraFirma(xml, PEM, digestValue) {
//         let signatureXmlFormat = '<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">';
//         let keyinfoXmlFormat =
//             '<KeyInfo>' +
//             '<X509Data>' +
//             '<X509Certificate>' +
//             PEM +
//             '</X509Certificate>' +
//             '</X509Data>' +
//             '</KeyInfo>';

//         let signedInfoXmlFormat =
//             '<SignedInfo>' +
//             '<CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" />' +
//             '<SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256" />' +
//             '<Reference URI="">' +
//             '<Transforms>' +
//             '<Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" />' +
//             '</Transforms>' +
//             '<DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" />' +
//             '<DigestValue>' +
//             digestValue +
//             '</DigestValue>' +
//             '</Reference>' +
//             '</SignedInfo>';
//         let firmado =
//             signatureXmlFormat + signedInfoXmlFormat + keyinfoXmlFormat + '</Signature>';
//         let indice = xml.search('</ECF>');
//         return xml.substring(0, indice) + firmado + xml.substring(indice);
//     }

//     convertToPem(p12ArrayBuffer, password) {
//         let p12Asn1 = forge.asn1.fromDer(p12ArrayBuffer);
//         let p12 = forge.pkcs12.pkcs12FromAsn1(p12Asn1, false, password);
//         let pemKey = this.getKeyFromP12(p12, password);
//         let certData = this.getCertificateFromP12(p12);
//         return {
//             pemKey: pemKey,
//             pemCertificate: certData.pemCertificate,
//             commonName: certData.commonName,
//         };
//     }

//     getKeyFromP12(p12, password) {
//         let keyData = p12.getBags({ bagType: forge.pki.oids.pkcs8ShroudedKeyBag }, password);
//         let pkcs8Key = keyData[forge.pki.oids.pkcs8ShroudedKeyBag][0] || keyData[forge.pki.oids.keyBag][0];
//         if (!pkcs8Key) throw new Error('Unable to get private key.');
//         let pemKey = forge.pki.privateKeyToPem(pkcs8Key.key).replace(/\r\n/g, '');
//         return pemKey;
//     }

//     getCertificateFromP12(p12) {
//         let certData = p12.getBags({ bagType: forge.pki.oids.certBag });
//         let certificate = certData[forge.pki.oids.certBag][0];
//         let pemCertificate = forge.pki.certificateToPem(certificate.cert).replace(/\r\n/g, '');
//         let commonName = certificate.cert.subject.attributes[0].value;
//         return { pemCertificate: pemCertificate, commonName: commonName };
//     }

//     c14nCanonicalization(node, options = {}) {
//         let defaultNs = options.defaultNs || "";
//         let defaultNsForPrefix = options.defaultNsForPrefix || {};
//         let ancestorNamespaces = options.ancestorNamespaces || [];
//         return this.c14nCanonicalizationInterno(node, [], defaultNs, defaultNsForPrefix, ancestorNamespaces);
//     }

//     c14nCanonicalizationInterno(node, prefixesInScope, defaultNs, defaultNsForPrefix, ancestorNamespaces) {
//         if (node.nodeType === 8) return this.renderComment(node);
//         if (node.data) return this.encodeSpecialCharactersInText(node.data);

//         let ns = this.renderNs(node, prefixesInScope, defaultNs, defaultNsForPrefix, ancestorNamespaces);
//         let res = ["<", node.tagName, ns.rendered, this.renderAttrs(node, ns.newDefaultNs), ">"];
//         for (let i = 0; i < node.childNodes.length; ++i) {
//             res.push(this.c14nCanonicalizationInterno(node.childNodes[i], [...prefixesInScope], ns.newDefaultNs, defaultNsForPrefix, []));
//         }
//         res.push("</", node.tagName, ">");
//         return res.join("");
//     }

//     renderComment(node) {
//         return `<!--${this.encodeSpecialCharactersInText(node.data)}-->`;
//     }

//     renderAttrs(node, defaultNS) {
//         let res = [];
//         if (node.attributes) {
//             let attrs = [...node.attributes].sort((a, b) => a.name.localeCompare(b.name));
//             attrs.forEach(attr => {
//                 if (attr.name.indexOf("xmlns") === 0) return;
//                 res.push(` ${attr.name}="${this.encodeSpecialCharactersInAttribute(attr.value)}"`);
//             });
//         }
//         return res.join("");
//     }

//     renderNs(node, prefixesInScope, defaultNs, defaultNsForPrefix, ancestorNamespaces) {
//         let res = [];
//         let newDefaultNs = defaultNs;

//         if (node.prefix && !prefixesInScope.includes(node.prefix)) {
//             prefixesInScope.push(node.prefix);
//             res.push(` xmlns:${node.prefix}="${node.namespaceURI || defaultNsForPrefix[node.prefix]}"`);
//         } else if (!node.prefix && defaultNs !== node.namespaceURI) {
//             newDefaultNs = node.namespaceURI;
//             res.push(` xmlns="${newDefaultNs}"`);
//         }
//         return { rendered: res.join(""), newDefaultNs };
//     }

//     encodeSpecialCharactersInText(text) {
//         return text.replace(/[&<>]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[char]));
//     }

//     encodeSpecialCharactersInAttribute(value) {
//         return value.replace(/[&<"]/g, char => ({ '&': '&amp;', '<': '&lt;', '"': '&quot;' }[char]));
//     }
// }

// module.exports = FirmaXMLService;


const fs = require('fs');
const forge = require('node-forge');
const xmldom = require('xmldom');

class FirmaXMLService {
    constructor() {}

    // Method to digitally sign an XML
    Firmar(xml, certifado, password) {
        let pem = this.convertToPem(certifado, password);
        let privateKey = forge.pki.privateKeyFromPem(pem.pemKey);

        let md = forge.md.sha256.create();
        var xmlData2 = new xmldom.DOMParser().parseFromString(xml);
        var xmlCanolizadoData2 = this.c14nCanonicalization(xmlData2.firstChild, null);
        md.update(xmlCanolizadoData2.toString(), 'utf8');

        let messageDigest = forge.util.encode64(md.digest().data);

        let pemXMLFormat = this.obtenerPEMXMLFormat(pem.pemCertificate);
        let xmlSinFirmado = this.agregarEstructuraFirma(
            xmlCanolizadoData2.toString(),
            pemXMLFormat,
            messageDigest
        );

        var xmlData = new xmldom.DOMParser().parseFromString(xmlSinFirmado);
        var xmlCanolizado = this.c14nCanonicalization(
            xmlData.getElementsByTagName("SignedInfo")[0],
            { defaultNsForPrefix: { ds: 'http://www.w3.org/2000/09/xmldsig#' } }
        );

        md = forge.md.sha256.create();
        md.update(xmlCanolizado.toString(), 'utf8');
        let signature = privateKey.sign(md);

        let signatureValue =
            '<SignatureValue>' + forge.util.encode64(signature) + '</SignatureValue>';
        let indiceFirma = xmlSinFirmado.search('</Signature>');
        let xmlFirmado =
            xmlSinFirmado.substring(0, indiceFirma) +
            signatureValue +
            xmlSinFirmado.substring(indiceFirma);

        return xmlFirmado;
    }

    obtenerPEMXMLFormat(PEM) {
        let PEMToXmlFormat = PEM.replace('-----BEGIN CERTIFICATE-----', '');
        PEMToXmlFormat = PEMToXmlFormat.replace('-----END CERTIFICATE-----', '');
        return PEMToXmlFormat;
    }

    agregarEstructuraFirma(xml, PEM, digestValue) {
        let signatureXmlFormat = '<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">';
        let keyinfoXmlFormat =
            '<KeyInfo>' +
            '<X509Data>' +
            '<X509Certificate>' +
            PEM +
            '</X509Certificate>' +
            '</X509Data>' +
            '</KeyInfo>';

        let signedInfoXmlFormat =
            '<SignedInfo>' +
            '<CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" />' +
            '<SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256" />' +
            '<Reference URI="">' +
            '<Transforms>' +
            '<Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" />' +
            '</Transforms>' +
            '<DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" />' +
            '<DigestValue>' +
            digestValue +
            '</DigestValue>' +
            '</Reference>' +
            '</SignedInfo>';
        let firmado =
            signatureXmlFormat + signedInfoXmlFormat + keyinfoXmlFormat + '</Signature>';
        let indice = xml.search('</ECF>');
        return xml.substring(0, indice) + firmado + xml.substring(indice);
    }

    convertToPem(p12ArrayBuffer, password) {
        let p12Asn1 = forge.asn1.fromDer(p12ArrayBuffer);
        let p12 = forge.pkcs12.pkcs12FromAsn1(p12Asn1, false, password);
        let pemKey = this.getKeyFromP12(p12, password);
        let certData = this.getCertificateFromP12(p12);
        return {
            pemKey: pemKey,
            pemCertificate: certData.pemCertificate,
            commonName: certData.commonName,
        };
    }

    getKeyFromP12(p12, password) {
        let keyData = p12.getBags({ bagType: forge.pki.oids.pkcs8ShroudedKeyBag }, password);
        let pkcs8Key = keyData[forge.pki.oids.pkcs8ShroudedKeyBag][0] || keyData[forge.pki.oids.keyBag][0];
        if (!pkcs8Key) throw new Error('Unable to get private key.');
        let pemKey = forge.pki.privateKeyToPem(pkcs8Key.key).replace(/\r\n/g, '');
        return pemKey;
    }

    getCertificateFromP12(p12) {
        let certData = p12.getBags({ bagType: forge.pki.oids.certBag });
        let certificate = certData[forge.pki.oids.certBag][0];
        let pemCertificate = forge.pki.certificateToPem(certificate.cert).replace(/\r\n/g, '');
        let commonName = certificate.cert.subject.attributes[0].value;
        return { pemCertificate: pemCertificate, commonName: commonName };
    }

    c14nCanonicalization(node, options = {}) {
        if (options === null) options = {};
        let defaultNs = options.defaultNs || "";
        let defaultNsForPrefix = options.defaultNsForPrefix || {};
        let ancestorNamespaces = options.ancestorNamespaces || [];
        return this.c14nCanonicalizationInterno(node, [], defaultNs, defaultNsForPrefix, ancestorNamespaces);
    }

    c14nCanonicalizationInterno(node, prefixesInScope, defaultNs, defaultNsForPrefix, ancestorNamespaces) {
        if (node.nodeType === 8) return `<!--${this.encodeSpecialCharactersInText(node.data)}-->`;
        if (node.data) return this.encodeSpecialCharactersInText(node.data);

        let ns = this.renderNs(node, prefixesInScope, defaultNs, defaultNsForPrefix, ancestorNamespaces);
        let res = ["<", node.tagName, ns.rendered, this.renderAttrs(node, ns.newDefaultNs), ">"];
        for (let i = 0; i < node.childNodes.length; ++i) {
            res.push(this.c14nCanonicalizationInterno(node.childNodes[i], [...prefixesInScope], ns.newDefaultNs, defaultNsForPrefix, []));
        }
        res.push("</", node.tagName, ">");
        return res.join("");
    }

    renderAttrs(node, defaultNS) {
        let res = [];
        if (node.attributes && node.attributes.length > 0) {
            let attrs = Array.from(node.attributes).sort((a, b) => a.name.localeCompare(b.name));
            attrs.forEach(attr => {
                if (attr.name.indexOf("xmlns") === 0) return;
                res.push(` ${attr.name}="${this.encodeSpecialCharactersInAttribute(attr.value)}"`);
            });
        }
        return res.join("");
    }

    renderNs(node, prefixesInScope, defaultNs, defaultNsForPrefix, ancestorNamespaces) {
        let res = [];
        let newDefaultNs = defaultNs;

        if (node.prefix && !prefixesInScope.includes(node.prefix)) {
            prefixesInScope.push(node.prefix);
            res.push(` xmlns:${node.prefix}="${node.namespaceURI || defaultNsForPrefix[node.prefix]}"`);
        } else if (!node.prefix && defaultNs !== node.namespaceURI) {
            newDefaultNs = node.namespaceURI;
            res.push(` xmlns="${newDefaultNs}"`);
        }
        return { rendered: res.join(""), newDefaultNs };
    }

    encodeSpecialCharactersInText(text) {
        return text.replace(/[&<>]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[char]));
    }

    encodeSpecialCharactersInAttribute(value) {
        return value.replace(/[&<"]/g, char => ({ '&': '&amp;', '<': '&lt;', '"': '&quot;' }[char]));
    }
}

(async () => {
    const args = process.argv.slice(2);

    if (args.length < 3) {
        console.error("Usage: node sign-xml.js <xmlFilePath> <certFilePath> <password>");
        process.exit(1);
    }

    const [xmlFilePath, certFilePath, password] = args;

    // try {
        const xml = fs.readFileSync(xmlFilePath, 'utf-8');
        const certData = fs.readFileSync(certFilePath);

        const firmaXMLService = new FirmaXMLService();
        const signedXml = firmaXMLService.Firmar(xml, certData.toString('binary'), password);

        const outputPath = "signed_output.xml";
        let _signedXml = signedXml.replace(`version="1.0" encoding="utf-8"`, '');
        _signedXml = xml.replace(`</SemillaModel>`, _signedXml);
        _signedXml += `</SemillaModel>`;
        fs.writeFileSync(outputPath, _signedXml);
        console.log(`Signed XML saved to: ${outputPath}`);
    // } catch (error) {
    //     console.error("Error signing XML:", error.message);
    //     process.exit(1);
    // }
})();