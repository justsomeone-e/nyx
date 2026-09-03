-- Put this LocalScript inside a ScreenGui in StarterGui
-- Name: UndertaleDialogue

local Players = game:GetService("Players")
local player = Players.LocalPlayer
local screenGui = script.Parent

-- Create the classic Undertale Black Box with White Border
local dialogFrame = Instance.new("Frame")
dialogFrame.Name = "DialogBox"
dialogFrame.Size = UDim2.new(0, 600, 0, 140)
dialogFrame.Position = UDim2.new(0.5, -300, 1, -160)
dialogFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
dialogFrame.BorderColor3 = Color3.fromRGB(255, 255, 255)
dialogFrame.BorderSizePixel = 4
dialogFrame.Parent = screenGui

local textLabel = Instance.new("TextLabel")
textLabel.Size = UDim2.new(1, -30, 1, -20)
textLabel.Position = UDim2.new(0, 15, 0, 10)
textLabel.BackgroundTransparency = 1
textLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
textLabel.TextSize = 20
textLabel.Font = Enum.Font.Code
textLabel.TextXAlignment = Enum.TextXAlignment.Left
textLabel.TextYAlignment = Enum.TextYAlignment.Top
textLabel.TextWrapped = true
textLabel.Text = ""
textLabel.Parent = dialogFrame

local function typeText(fullText)
    textLabel.Text = ""
    for i = 1, #fullText do
        textLabel.Text = string.sub(fullText, 1, i)
        task.wait(0.03)
    end
end

task.spawn(function()
    task.wait(1)
    typeText("* 03:17 AM. You stand in the snowy mountain pass.\n* A nylon acoustic guitar hangs cold on your back.\n* The wind carries a ragged whisper: 'Where did you sleep last night?'")
end)
