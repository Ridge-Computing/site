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

def format(content)
    temp = []
    content.split(/\\\\/).each do |sub|
        temp << emojify(sub)
    end
    Kramdown::Document.new(temp.join('\\\\')).to_html.gsub('<ul>', '<ul style="list-style-type: disc!important; margin-left: 1em;">').gsub('<p>', '<br><p>').sub! '<br>', ''
end

uuid = ARGV[0]

if db.hexists uuid, 'bio'
    File.write "app/templates/uuid/#{uuid}.html", format(db.hget uuid, 'bio')
elsif db.hexists uuid, 'description'
    File.write "app/templates/uuid/#{uuid}.html", format(db.hget uuid, 'description')
end
