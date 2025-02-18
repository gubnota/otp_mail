from email.message import Message
from email.parser import BytesParser
from email import policy
from email.utils import parsedate_to_datetime
import os
import re

import quopri
import codecs

# import html2text
# from bs4 import BeautifulSoup


# def convert_html_to_text(html_content):
#     """Converts HTML content to plain text."""
#     soup = BeautifulSoup(html_content, "html.parser")
#    return soup.get_text()


# https://github.com/sensidev/eml2text/blob/main/eml2text.py


def extract_text_and_metadata_from_eml(msg: Message, remove_links=True):
    # msg = BytesParser(policy=policy.default).parse(msg_text)
    # msg = BytesParser(policy=policy.default).parse(fp)
    """Extracts all headers, date, and plain text from an .eml file, logging a warning if attachments are ignored."""
    # with open(eml_file, "rb") as file:
    #     msg = BytesParser(policy=policy.default).parse(file)

    # Extract metadata (headers)
    headers = {
        "From": msg["From"].encode("utf-8").decode("utf-8"),
        "To": msg["To"].encode("utf-8").decode("utf-8"),
        "Subject": msg["Subject"].encode("utf-8").decode("utf-8").replace("\n", " "),
        "Date": msg["Date"].encode("utf-8").decode("utf-8"),
    }

    # Parse the date header to a datetime object
    email_date = parsedate_to_datetime(headers["Date"])

    text_content = ""

    # Extract the email's body
    attachment_found = False
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                text_content += part.get_payload(decode=True).decode(
                    part.get_content_charset("utf-8")
                )
            elif part.get_content_disposition() == "attachment":
                attachment_found = True
    else:
        text_content += msg.get_payload(decode=True).decode(
            msg.get_content_charset("utf-8")
        )

    if remove_links:
        text_content = re.sub(r"http[s]?://\S+", "", text_content)
    # Log warning if attachment was found and ignored
    if attachment_found:
        print(f"Warning: The email contains one or more attachments that were ignored.")

    # Convert HTML parts to text
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                html_content = part.get_payload(decode=True).decode(
                    part.get_content_charset("utf-8")
                )
                text_content += html_content
                # html2text.html2text(html_content)  # convert_html_to_text(html_content)
    text_content = text_content.strip()
    text_content = re.sub(r"[\s]+", " ", text_content)
    text_content = (
        "\n".join(f"{key}: {value}" for key, value in headers.items()) + "\n\n"
    ) + text_content
    text_content = re.sub(r"[\n]+", "\n", text_content)
    print(text_content[:4095])
    return text_content[:4095]


def decode_encoded_string(
    encoded_string="""=?UTF-8?Q?Andreas_Lind=C3=A9n_reacted_to_a_pos?=
    =?UTF-8?Q?t:_Har_ni_en_id=C3=A9=3F=0A=0A=0A=0A=0AH=C3=B6r_av_er=E2=80=A6?=""",
):
    # Split the string into parts and decode each part
    parts = encoded_string.split("\n")
    decoded_parts = []

    for part in parts:
        # Extract the encoded part
        start = part.find("Q?") + 2
        end = part.find("?=")
        if start != -1 and end != -1:
            encoded_part = part[start:end]
            # Decode quoted-printable
            decoded_bytes = quopri.decodestring(encoded_part)
            # Decode bytes using UTF-8
            decoded_string = decoded_bytes.decode("utf-8")
            decoded_parts.append(decoded_string)

    # Join the decoded parts into a single string
    final_string = "".join(decoded_parts)
    final_string = re.sub(r"[\n]+", "\n", final_string)
    return final_string


if __name__ == "__main__":
    # with open("./email.eml", "rb") as file:
    #     msg = BytesParser(policy=policy.default).parse(file)  # email_date,
    # text_content = extract_text_and_metadata_from_eml(msg, remove_links=True)
    # print(email_date)
    # print(text_content)
    print(decode_encoded_string())
