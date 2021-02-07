require 'gemoji'
require 'kramdown'
require 'redis'

db = Redis.new

def emojify(content)
    content.to_str.gsub(/(?<!\\):([\w+-]+):/) do |match|
        if emoji = Emoji.find_by_alias($1)
            emoji.raw
        else
            match
        end
    end
end

# def sup(content)
#     content.to_str.gsub(/(?<!\\)\^\((.+)(?<!\\)\)/) do |match|
#         '<sup markdown="1">' << $1 << '</sup>'
#     end
# end
#
# def sub(content)
#     content.to_str.gsub(/(?<!\\)_\((.+)(?<!\\)\)/) do |match|
#         '<sub markdown="1">' << $1 << '</sub>'
#     end
# end
#
# def strike(content)
#     content.to_str.gsub(/(?<!\\)~~(.+)(?<!\\)~~/) do |match|
#         '<s markdown="1">' << $1 << '</s>'
#     end
# end
#
# def under(content)
#     content.to_str.gsub(/(?<!\\)__(.+)(?<!\\)__/) do |match|
#         '<u markdown="1">' << $1 << '</u>'
#     end
# end

def format(content)
    content.gsub!(/\\\\/, '&#92;')
#     content = under(strike(sup(sub(emojify(content)))))
    content = emojify(content)
    content.gsub!(/\\\^/, '^').gsub!(/\\~/, '~').gsub!('&#92;', '\\\\')
    doc = Kramdown::Document.new(content).to_html.gsub('<ul>', '<ul style="list-style-type: disc!important; margin-left: 1em;">').gsub('<p>', '<br><p>').gsub(' markdown="1"', '')
    if doc[0..3].eql? '<br>'
        doc[4..-1]
    else
        doc
    end
end

uuid = ARGV[0]

if db.hexists uuid, 'bio'
    File.write "app/templates/uuid/#{uuid}.html", format(db.hget uuid, 'bio')
elsif db.hexists uuid, 'description'
    File.write "app/templates/uuid/#{uuid}.html", format(db.hget uuid, 'description')
end
