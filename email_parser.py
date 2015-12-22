import os
import sys
import re
import pdb


class EmailParser:
    warnings = []

    def __init__(self, filename):
        self._source = self._read_file(filename)
        self.from_regex = re.compile(
            r"\bfrom:?(\s.*\s)?\<?([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\>?\b",
            flags=re.IGNORECASE)
        self.to_regex = re.compile(
            r"\b(to:?\s?(?:[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:\,\s*)?)+)\b",
            flags=re.IGNORECASE)
        self.email_regex = re.compile(
            r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b",
            flags=re.IGNORECASE)
        self.url_regex = re.compile(
            r"\b((https?|ftp)://[^\s/$.?#].[^\s|\"|\<]*\b)",
            flags=re.IGNORECASE)

    def _read_file(self, filename):
        if not os.path.isfile(filename):
            raise Exception('there are no file with such name: %' % filename)
        data = open(filename, 'r').read()
        if len(data) == 0:
            raise Exception('the file is empty')
        return data

    def _parse_from(self):
        'parse string in form: "From: email@address"'
        fr = re.findall(self.from_regex, self._source)
        if len(fr) == 0:
            self.warnings.append(
                'There are no "From: " declaration! or email is not valid')
        return [fr[0][1]]

    def _parse_to(self):
        #pdb.set_trace()
        'parse string in form: "To: email@address"'
        to = ' '.join(re.findall(self.to_regex, self._source))
        to_emails = re.findall(self.email_regex, to)
        if len(to_emails) == 0:
            self.warnings.append(
                'There are no "To:" declaration! or email is not valid')
        return to_emails

    def _parse_emails(self):
        'parse emails in the file that matches regex'
        return re.findall(self.email_regex, self._source)

    def _parse_urls(self):
        #pdb.set_trace()
        urls = [t[0] for t in re.findall(self.url_regex, self._source)]
        return urls

    def parse(self):
        """
        parse emails and URLs from email.
        we suppose that body starts with 'Body:' declaration
        """

        if 'Body:' not in self._source:
            self.warnings.append('There are no body in message!')
        result = """
        From: {fr}
        To: {to}
        Emails: {emails}
        URLs: {urls}
        Total e-mail addresses: {email_cnt}
        Total URLs: {url_cnt}
        """.format(
            fr = ','.join(self._parse_from()) or 'empty',
            to = ','.join(self._parse_to()) or 'empty',
            emails = ',\n\t\t'.join(self._parse_emails()) or 'no emails',
            urls = ',\n\t\t'.join(self._parse_urls()) or 'no URLs',
            email_cnt = len(self._parse_emails()),
            url_cnt = len(self._parse_urls()),
            )
        return result


def main():
    if len(sys.argv) == 1:
        raise Exception('please specify path to file as first argument')
    filename = sys.argv[1]
    parser = EmailParser(filename)
    print parser.parse()
    if parser.warnings:
        print 'Warnings: \n%s' % '\n-'.join(parser.warnings)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print "Error: %s" % e.message
